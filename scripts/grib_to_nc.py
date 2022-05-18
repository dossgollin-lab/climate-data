import argparse
from numpy import float32

import xarray as xr


def main():

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", type=str)
    parser.add_argument("--lonmin", type=float)
    parser.add_argument("--lonmax", type=float)
    parser.add_argument("--latmin", type=float)
    parser.add_argument("--latmax", type=float)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    ds = (
        xr.load_dataarray(args.infile)
        .sel(
            longitude=slice(args.lonmin, args.lonmax),
            latitude=slice(args.latmax, args.latmin),
        )
        .astype(float32)
    )
    ds.name = "precip_rate"
    ds.to_netcdf(args.outfile, format="netcdf4")


if __name__ == "__main__":
    main()
