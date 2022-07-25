import os
from datetime import datetime
import logging
from tqdm import tqdm
from typing import NamedTuple, Union


import numpy as np
import pandas as pd
import xarray as xr

from .const import MISSING_SNAPSHOTS
from .namingconventions import *
from .util import download_file, unzip_gz, delete_file, ensure_dir


class BoundingBox:
    def __init__(
        self,
        lonmin: float = 230,
        lonmax: float = 300,
        latmin: float = 20,
        latmax: float = 55,
    ) -> None:
        """
        Bounding box for the data to retain.
        The valid boundaries are lon in [230, 300] and lat in [20, 55]
        """

        self.latmin = latmin
        self.latmax = latmax
        self.lonmin = lonmin
        self.lonmax = lonmax

        self.assert_valid_longitudes()
        self.assert_valid_latitudes()

    def assert_valid_longitudes(self) -> None:
        """Make sure the longitudes are valid"""
        assert (
            self.lonmin < self.lonmax
        ), "min longitude must be less than max longitude"
        assert self.lonmin >= 230, "min longitude must be at least 230"
        assert self.lonmax <= 300, "max longitude must be no greater than 300"

    def assert_valid_latitudes(self) -> None:
        """Make sure the latitudes are valid"""
        assert self.latmin < self.latmax, "min latitude must be less than max latitude"
        assert self.latmin >= 20, "min latitude must be at least 20"
        assert self.latmax <= 55, "max latitude must be at least 55"


def assert_valid_datetime(dt: datetime) -> None:
    """
    Do any needed checks on the data
    """
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    assert dt >= GAUGECORR_BEGINTIME, f"Data is not available for {dt_str}"
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0


class TimeRange:
    """Shallow rapper for pandas.date_range with some checks"""

    def __init__(self, stime: datetime, etime: datetime) -> None:

        assert_valid_datetime(stime)
        assert_valid_datetime(etime)
        self.dts = pd.date_range(stime, etime, freq="H")


def assert_valid_path(path: str) -> None:
    """Make sure the path is valid"""
    assert os.path.isdir(path), f"invalid path given: {path}"


def bbox_equal(ds: xr.DataArray, bbox: BoundingBox):
    """
    Check if the bounding box of the data is equal to the given bounding box
    """
    delta = 0.1

    lonmin = ds.longitude.min()
    lonmax = ds.longitude.max()
    latmin = ds.latitude.min()
    latmax = ds.latitude.max()

    return (
        bbox.lonmin <= lonmin <= bbox.lonmin + delta
        and bbox.lonmax >= lonmax >= bbox.lonmax - delta
        and bbox.latmin <= latmin <= bbox.latmin + delta
        and bbox.latmax >= latmax >= bbox.latmax - delta
    )


class PrecipSnapshot:
    def __init__(self, dt: datetime, dirname: str, bbox: BoundingBox) -> None:

        # check inputs
        assert_valid_datetime(dt)
        assert_valid_path(dirname)

        self.dt = dt
        self.bbox = bbox
        self.date: Union[xr.DataArray, None] = None  # initialize with blank data

        dirname = os.path.abspath(dirname)  # track relative paths
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        self._grib2_fname = os.path.join(dirname, get_grib2_fname(self.dt))
        self._gz_fname = os.path.join(dirname, get_gz_fname(self.dt))
        self._nc_fname = os.path.join(dirname, get_nc_fname(self.dt))

        # the grib2 file is unchanged so if it exists it should be right
        self._grib2_loaded = os.path.isfile(self._grib2_fname)

        # the netcdf4 file depends on the bounding box
        self._nc_loaded = False
        if os.path.isfile(self._nc_fname):
            ds = xr.open_dataset(self._nc_fname)
            if bbox_equal(ds, self.bbox):
                self._nc_loaded = True

    def _download_grib2(self) -> None:
        """Download the grib2 data and save to file"""
        url = get_url(self.dt)

        logging.info(f"Downloading data from {url} and saving to {self._gz_fname}")
        download_file(url=url, fname=self._gz_fname)

        logging.info(f"Unzipping from {self._gz_fname} to {self._grib2_fname}")
        unzip_gz(fname_in=self._gz_fname, fname_out=self._grib2_fname)
        delete_file(self._gz_fname)
        self._grib2_fname = self._grib2_fname

    def _extract_nc(self, bbox: BoundingBox) -> None:
        """Extract the netcdf4 data, trim to bounding box, and save to file"""

        assert self._grib2_fname, "grib2 file not found"

        logging.info(
            f"Extracting netcdf4 data from {self._grib2_fname} to {self._nc_fname}"
        )
        ds = (
            xr.load_dataarray(self._grib2_fname)
            .sel(
                longitude=slice(self.bbox.lonmin, self.bbox.lonmax),
                latitude=slice(self.bbox.latmax, self.bbox.latmin),
            )
            .astype(np.float32)
        )
        ds = ds.where(
            ds != -3
        )  # add a mask for missing data TODO: should be a better way
        ds.name = "precip_rate"
        ds.to_netcdf(self._nc_fname, format="netcdf4")
        self._nc_loaded = True

    def ensure_data(self) -> None:
        """Make sure the grib2 and netcdf files are where they should be"""
        if not self._grib2_loaded:
            self._download_grib2()
        if not self._nc_loaded:
            self._extract_nc(self.bbox)

    @property
    def data(self) -> xr.Dataset:
        """Get the snapshot's data"""
        if self._nc_loaded:
            return xr.open_dataset(self._nc_fname)
        else:
            raise ValueError("File {self._nc_fname} not yet created")


class PrecipDataSet:
    def __init__(self, trange: TimeRange, bbox: BoundingBox, dirname: str) -> None:

        self.trange = trange
        self.bbox = bbox
        ensure_dir(dirname)
        self._dirname = dirname
        self.data: Union[xr.DataArray, None] = None  # initialize blank
        self._snapshots = [
            PrecipSnapshot(dt=dt, dirname=self._dirname, bbox=self.bbox)
            for dt in self.trange.dts
        ]

    def get_data(self) -> xr.DataArray:
        """Read in the data from each snapshot"""

        # TODO parallelize this step
        # make sure each data point has accessed the data
        for snapshot in tqdm(self._snapshots):
            snapshot.ensure_data()

        # load all the data as an mfdataset
        return xr.open_mfdataset(
            [snapshot._nc_fname for snapshot in self._snapshots],
            combine="nested",
            concat_dim="time",
            chunks={"time": 10},
        ).sortby("time")["precip_rate"]
