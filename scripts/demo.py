from datetime import datetime
from genericpath import isfile
import logging
import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import codebase


def main():

    # configure what gests logged
    logging.basicConfig(filename="demo.log", level=logging.INFO)

    # define the bounding box for the data
    bbox = codebase.BoundingBox(
        lonmin=260,
        lonmax=290,
        latmin=25,
        latmax=40,
    )

    # define time boundaries
    trange = codebase.TimeRange(
        stime=datetime(2020, 10, 13, 0), etime=datetime(2020, 10, 14, 12)
    )

    # create the (abstract dataset)
    dataset = codebase.PrecipDataSet(
        trange=trange,
        bbox=bbox,
        dirname=os.path.join(os.path.curdir, "data", "external"),
    )

    # get the data and save to netcdf4
    ds = dataset.get_data()
    fname = os.path.join(dataset._dirname, "demo.nc")
    if os.path.isfile(fname):
        os.remove(fname)
    ds.to_netcdf(fname, format="netcdf4")

    # make a pretty plot and save it
    ds.mean(dim="time", skipna=True).plot()
    plt.savefig(os.path.join(dataset._dirname, "demo.png"))


if __name__ == "__main__":
    main()
