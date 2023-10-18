"""
This script will download ONE YEAR OF ERA5 HOURLY REANALYSIS DATA over the given domain
(defaults to CONUS). Storing one year of data in one file makes it easier to work with
and more resilient to errors in downloading.

You need to specify the year, the output file name, the variable, and the pressure level.
Optionally, specify the domain. The default domain is CONUS.

The variable should follow the ERA5 documentation. Some common ones: 
- 2m_temperature
- u_component_of_wind

To access the data you will need a password saved in a local file. See CDASAPI
documentation for details!

ADDITIONAL DOCUMENTATION:

ERA5 documentation: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
cdsapi documentation: https://cds.climate.copernicus.eu/api-how-to
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
    parser.add_argument("--variable", type=str)
    parser.add_argument("--year", type=int)
    parser.add_argument("--resolution", type=float)
    parser.add_argument("--lonmin", type=float, default=CONUS[0][0])
    parser.add_argument("--lonmax", type=float, default=CONUS[0][1])
    parser.add_argument("--latmin", type=float, default=CONUS[1][0])
    parser.add_argument("--latmax", type=float, default=CONUS[1][1])
    args = parser.parse_args()

    dataset = "reanalysis-era5-single-levels"
    product_type = "reanalysis"
    months = [f"{month:02d}" for month in range(1, 13)]  # 01, 02, ..., 12
    days = [f"{day}" for day in np.arange(1, 32)]  # 1, 2, ..., 31
    hours = [f"{hour:02d}:00" for hour in range(24)]  # 00:00, 01:00, ... 23:00
    bbox = [args.latmax, args.lonmin, args.latmin, args.lonmax]
    grid = [args.resolution, args.resolution]

    ecmwf_client = cdsapi.Client()
    ecmwf_client.retrieve(
        dataset,
        {
            "product_type": product_type,
            "format": "netcdf",
            "variable": args.variable,
            "year": [args.year],
            "month": months,
            "day": days,
            "time": hours,
            "area": bbox,
            "grid": grid,
        },
        args.outfile,
    )


if __name__ == "__main__":
    main()
