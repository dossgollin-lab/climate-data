"""
A trivial example that reads in all the available data
"""

import argparse
from datetime import datetime
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr

# create infrastructure to read the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--path",
    help="where is the folder containing the data",
    type=str,
    default="data/external",
)
parser.add_argument("--outfile", help="where to save output figure", type=str)


def main():

    # parse the command line arguments
    args = parser.parse_args()

    # load all the data as an mfdataset
    ds = (
        xr.open_mfdataset(
            os.path.join(args.path, "*.nc"),
            combine="nested",
            concat_dim="time",
            chunks={"time": 10},
        )
        .sortby("time")
        .rename({"param9.6.209": "prcp_rate"})["prcp_rate"]
    )

    harvey = (
        ds.sel(time=slice(datetime(2017, 8, 25, 0), datetime(2017, 8, 28, 23)))
        .resample(time="1D")  # resample to daily
        .sum(skipna=False)  # take the daily sum
        .rename({"time": "date"})
    )
    harvey.name = "Precipitation [mm]"

    # plot the first time step of the dataset
    p = harvey.plot(
        transform=ccrs.PlateCarree(),
        col="date",
        col_wrap=2,
        subplot_kws={"projection": ccrs.PlateCarree()},
        figsize=(12, 6),
    )

    for ax in p.axes.flat:
        ax.add_feature(cfeature.STATES)

    plt.savefig(args.outfile)


if __name__ == "__main__":
    main()
