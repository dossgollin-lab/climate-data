from datetime import datetime
from genericpath import isfile
import logging
import os

import cartopy.crs as ccrs
from cartopy.feature import STATES
import matplotlib.pyplot as plt

import codebase


def main():

    # configure what gests logged
    logging.basicConfig(filename="demo.log", level=logging.INFO)

    # define the bounding box for the data -- this is roughly Texas
    bbox = codebase.BoundingBox(
        lonmin=260,
        lonmax=290,
        latmin=25,
        latmax=40,
    )

    # define time boundaries -- August 2017 is when Harvey happened
    trange = codebase.TimeRange(
        stime=datetime(2017, 8, 1, 0), etime=datetime(2017, 8, 31, 23)
    )

    # create the dataset abstraction
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
    p = ds.sum(dim="time", skipna=True).plot(
        subplot_kws=dict(projection=ccrs.PlateCarree()),
        transform=ccrs.PlateCarree(),
        cmap="magma_r",
    )
    plt.title(f"Total Precip, {trange.printbounds()}")
    p.axes.coastlines()
    p.axes.add_feature(STATES, edgecolor="black", linewidth=0.5)
    plt.savefig(os.path.join(os.curdir, "demo.png"))


if __name__ == "__main__":
    main()
