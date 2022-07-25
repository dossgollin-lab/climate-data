import datetime
import os
from tqdm import tqdm
from typing import NamedTuple, Union
from urllib.request import urlretrieve

from numpy import float32
import pandas as pd
import xarray as xr

from .const import MISSING_SNAPSHOTS
from .namingconventions import *


class BoundingBox:
    def __init__(
        self,
        lonmin: float,
        lonmax: float,
        latmin: float,
        latmax: float,
    ) -> None:

        assert latmax > latmin
        assert -90 <= latmax <= 90
        assert -90 <= latmin <= 90

        assert lonmax > lonmin
        assert 0 <= lonmin <= 360
        assert 0 <= lonmax <= 360

        self.latmin = latmin
        self.latmax = latmax
        self.lonmin = lonmin
        self.lonmax = lonmax


def assert_valid_datetime(dt: datetime.datetime) -> None:
    """
    Do any needed checks on the data
    """
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    assert dt >= STIME, f"Data is not available for {dt_str}"
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0


class TimeRange:
    """Shallow rapper for pandas.date_range with some checks"""

    def __init__(self, stime: datetime.datetime, etime: datetime.datetime) -> None:

        assert_valid_datetime(stime)
        assert_valid_datetime(etime)
        self.dts = pd.date_range(stime, etime, freq="H")


# TODO: is there a better type for paths / way to handle them?
def assert_valid_path(path: str) -> None:
    """Make sure the path is valid"""
    assert os.path.exists(path), "invalid path given"


class PrecipSnapshot:
    def __init__(self, dt: datetime.datetime, dirname: str, bbox: BoundingBox) -> None:

        # check inputs
        assert_valid_datetime(dt)
        assert_valid_path(dirname)

        self.dt = dt
        self.bbox = bbox
        self.date: Union[xr.DataArray, None] = None  # initialize with blank data

        self._data_loaded = False
        self._dirname = os.path.abspath(dirname)  # track relative paths
        self._grib2_fname: Union[str, None] = None  # is the grib2 file downloaded?
        self._nc_fname: Union[str, None] = None

    def _download_grib2(self) -> None:
        """Download the grib2 data and save to file"""
        fname = get_grib2_fname(self.dt)
        raise NotImplementedError
        self._grib2_fname = os.path.join(self._dirname, fname)

    def _extract_nc(self, bbox: BoundingBox) -> None:
        """Extract the netcdf4 data, trim to bounding box, and save to file"""

        assert self._grib2_fname, "grib2 file not found"
        nc_fname = get_nc_fname(self.dt)
        ds = (
            xr.load_dataarray(self._grib2_fname)
            .sel(
                longitude=slice(self.bbox.lonmin, self.bbox.lonmax),
                latitude=slice(self.bbox.latmax, self.bbox.latmin),
            )
            .astype(float32)
        )
        ds.name = "precip_rate"
        ds.to_netcdf(nc_fname, format="netcdf4")
        self._nc_fname = os.path.join(self._dirname, nc_fname)

    def ensure_data(self) -> None:
        """Make sure the grib2 and netcdf files are where they should be"""
        if not self._grib2_fname:
            self._download_grib2()
        if not self._nc_fname:
            self._extract_nc(self.bbox)
        self._data_loaded = True

    @property
    def data(self) -> xr.Dataset:
        """Get the snapshot's data"""
        if self._data_loaded:
            return xr.open_dataset(self._nc_fname)
        else:
            raise ValueError("File {self._nc_fname} not yet created")


class PrecipDataSet:
    def __init__(self, trange: TimeRange, bbox: BoundingBox, dirname: str) -> None:

        self.trange = trange
        self.bbox = bbox
        assert_valid_path(dirname)
        self._dirname = dirname
        self.data: Union[xr.DataArray, None] = None  # initialize blank
        self._snapshots = [
            PrecipSnapshot(dt=dt, dirname=self._dirname, bbox=self.bbox)
            for dt in self.trange.dts
        ]

    def get_data(self) -> xr.Dataset:
        """Read in the data from each snapshot"""

        # TODO parallelize?
        # make sure each data point has accessed the data
        for snapshot in tqdm(self._snapshots):
            snapshot.ensure_data()

        # load all the data as an mfdataset
        return xr.open_mfdataset(
            [snapshot._nc_fname for snapshot in self._snapshots],
            combine="nested",
            concat_dim="time",
        ).sortby("time")
