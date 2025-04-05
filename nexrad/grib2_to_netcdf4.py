import argparse
import xarray as xr
import os

def subset_and_convert(input_file, output_file, lon_min, lon_max, lat_min, lat_max):
    """
    Subset a GRIB2 file and save it as a NetCDF4 file.
    """
    # Open the GRIB2 file
    ds = xr.open_dataset(input_file, engine="cfgrib", decode_timedelta=False)

    # Subset the data
    ds_subset = ds.sel(longitude=slice(lon_min, lon_max), latitude=slice(lat_max, lat_min))

    # Save the subset as a NetCDF4 file
    ds_subset.to_netcdf(output_file, format="NETCDF4")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subset a GRIB2 file and save as NetCDF4.")
    parser.add_argument("--input", required=True, help="Path to the input GRIB2 file.")
    parser.add_argument("--output", required=True, help="Path to the output NetCDF4 file.")
    parser.add_argument("--lonmin", type=float, required=True, help="Minimum longitude of the bounding box.")
    parser.add_argument("--lonmax", type=float, required=True, help="Maximum longitude of the bounding box.")
    parser.add_argument("--latmin", type=float, required=True, help="Minimum latitude of the bounding box.")
    parser.add_argument("--latmax", type=float, required=True, help="Maximum latitude of the bounding box.")

    args = parser.parse_args()

    subset_and_convert(
        input_file=args.input,
        output_file=args.output,
        lon_min=args.lonmin,
        lon_max=args.lonmax,
        lat_min=args.latmin,
        lat_max=args.latmax,
    )