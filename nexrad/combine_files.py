import argparse
import numpy as np
import xarray as xr
import pandas as pd


def concatenate_files(input_files, output_file, year, month):
    # Open multiple datasets as one
    datasets = xr.open_mfdataset(input_files, combine="by_coords")

    # Create a date range that explicitly spans the entire month
    start_time = f"{year}-{month:02}-01 00:00"
    end_time = f"{year}-{month:02}-{pd.Timestamp(year, month, 1).days_in_month} 23:00"
    all_hours = pd.date_range(start=start_time, end=end_time, freq="H")

    # Reindex to ensure data exists for all hours of the month
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
    parser.add_argument("year", type=int, help="Year of the data.")
    parser.add_argument("month", type=int, help="Month of the data.")
    args = parser.parse_args()

    concatenate_files(args.input_files, args.output_file, args.year, args.month)
