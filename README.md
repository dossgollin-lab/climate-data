# NEXRAD-xarray

This is a **work in progress**!
Use this software **with caution**!
If you find it helpful please consider using the `Issues` tab to identify problems or suggest improvements.

The NOAA NEXRAD radar precipitation data is very useful for many hydrological applications, but it's stored in a confusing structure on a server hosted by Iowa State.
The individual files are stored as `.grib2` files, which has the advantage of keeping their size small but the disadvantage of being hard to use with the `dask`/`xarray` parallel processing pipeline.

This program creates a database of NEXRAD radar precipitation data in formats that are easy to use for analysis, specifically Netcdf4 files that play nicely with the [Pangeo](https://pangeo.io/) ecosystem and can be stored on a local hard drive.

## Data variables

We use the `MultiSensor_QPE_01H_Pass2` dataset when available and the `GaugeCorr_QPE_01H` for earlier periods.
See [docs](./doc/) for more information.

## Pre-Requisites

You will need the following:

1. Anaconda Python
1. The `curl` utility (you probably have it!)
1. The [CDO Tool](https://code.mpimet.mpg.de/projects/cdo/wiki#Installation-and-Supported-Platforms) which is available on nearly all platforms

## Approach

1. We use [Snakemake](https://snakemake.readthedocs.io/) to develop a reproducible data organization structure
1. We use the custom package defined in `codebase/` to handle some of the annoying variable naming conventions

The basic steps of the analysis are

1. Download the `.grib2.gz` file from the Iowa State repository
1. Unzip the file from `.grib2.gz` to `.grib2`
1. Use the `cdo` tool to convert from `.grib2` to NetCDF 4 (`.nc`)
1. Leverage the `open_mfdataset` functionality in `xarray` to handle datasets spread across many files
