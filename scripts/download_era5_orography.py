"""
This script will download ERA5 orography data.

Details: see
https://confluence.ecmwf.int/pages/viewpage.action?pageId=228854952
"""

import argparse

import cdsapi
import numpy as np

# the default domain corresponds to CONUS
CONUS = [(-125, -65), (25, 50)]


def main() -> None:
    """Run everything"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=str)
    parser.add_argument("--resolution", type=float)
    parser.add_argument("--lonmin", type=float, default=CONUS[0][0])
    parser.add_argument("--lonmax", type=float, default=CONUS[0][1])
    parser.add_argument("--latmin", type=float, default=CONUS[1][0])
    parser.add_argument("--latmax", type=float, default=CONUS[1][1])
    args = parser.parse_args()

    ecmwf_client = cdsapi.Client()
    ecmwf_client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "geopotential",
            "year": "2018",
            "month": "01",
            "day": "01",
            "time": "00:00",
            "area": [args.latmax, args.lonmin, args.latmin, args.lonmax],
            "format": "netcdf",
            "grid": [args.resolution, args.resolution],
        },
        args.outfile,
    )


if __name__ == "__main__":
    main()
