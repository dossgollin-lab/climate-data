"""
A trivial example that reads in all the available data
"""

import xarray as xr


def main():

    # load all the data as an mfdataset
    ds = (
        xr.open_mfdataset(
            "data/external/*.nc",
            combine="nested",
            concat_dim="time",
            chunks={"time": 10},
        )
        .sortby("time")
        .rename({"param9.6.209": "prcp_rate"})["prcp_rate"]
    )

    # print the dataset
    print(ds)


if __name__ == "__main__":
    main()
