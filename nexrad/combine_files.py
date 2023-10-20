import numpy as np
import xarray as xr
import pandas as pd
import os


def concatenate_files(input_files, output_dir, year, month, bounding_boxes):
    # Open multiple datasets as one
    datasets = (
        xr.open_mfdataset(input_files, combine="by_coords")
        .sortby("time")
        .isel(alt=0)
        .drop("alt")
    )

    for var in ["param9.6.209", "param37.6.209"]:
        if var in datasets.data_vars:
            datasets = datasets.rename({var: "precip"})
            break

    # Create a date range that explicitly spans the entire month
    start_time = f"{year}-{month:02}-01 00:00"
    end_time = f"{year}-{month:02}-{pd.Timestamp(year, month, 1).days_in_month} 23:00"
    all_hours = pd.date_range(start=start_time, end=end_time, freq="H")

    # Reindex to ensure data exists for all hours of the month
    datasets = datasets.reindex(time=all_hours, fill_value=np.nan).sortby("time")

    # Loop through each bounding box and save a subset of the dataset
    for bbox in bounding_boxes:
        subset = datasets.sel(
            lon=slice(bbox["lon_min"], bbox["lon_max"]),
            lat=slice(bbox["lat_min"], bbox["lat_max"]),
        )
        output_file = os.path.join(
            output_dir, f"data_{bbox['name']}_{year}_{month:02}.nc"
        )
        subset.load().to_netcdf(output_file, format="NETCDF4")

    # Close the datasets
    datasets.close()


if __name__ == "__main__":
    # Use the snakemake object to get inputs, outputs, and parameters
    input_files = snakemake.input
    output_dir = snakemake.params.output_dir
    year = snakemake.params.year
    month = snakemake.params.month
    bounding_boxes = snakemake.config["bounding_boxes"]

    concatenate_files(input_files, output_dir, year, month, bounding_boxes)
