import argparse
import numpy as np
import xarray as xr
import pandas as pd


def concatenate_files(input_files, output_file):
    # Open multiple datasets as one
    datasets = xr.open_mfdataset(input_files, combine="by_coords")

    # Identify the year from the data
    year = pd.to_datetime(datasets.time.values[0]).year

    # Create a date range that explicitly spans the entire year
    all_hours = pd.date_range(
        start=f"{year}-01-01 00:00", end=f"{year}-12-31 23:00", freq="H"
    )

    # Reindex to ensure data exists for all hours of the year
    datasets = datasets.reindex(time=all_hours, fill_value=np.nan).sortby("time")

    # Save the combined dataset
    datasets.to_netcdf(output_file)

    # Close the datasets
    datasets.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate netCDF files.")
    parser.add_argument(
        "input_files",
        type=str,
        nargs="+",
        help="List of input netCDF files to concatenate.",
    )
    parser.add_argument(
        "output_file", type=str, help="Output file path for the concatenated result."
    )
    args = parser.parse_args()

    concatenate_files(args.input_files, args.output_file)
