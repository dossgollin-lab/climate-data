# NEXRAD-xarray

This is a **work in progress**!
Use this software **with caution**!
If you find it helpful please consider using the `Issues` tab to identify problems or suggest improvements.

The NOAA NEXRAD radar precipitation data is very useful for many hydrological applications, but it's stored in a confusing structure on a server hosted by Iowa State.
The individual files are stored as `.grib2` files, which has the advantage of keeping their size small but the disadvantage of being hard to use with the `dask`/`xarray` parallel processing pipeline ()
This program will create a database of NEXRAD radar precipitation data in formats that are easy to use for analysis, specifically Netcdf4 files that play nicely with the [Pangeo](https://pangeo.io/) ecosystem and can be stored on a local hard drive.
Specifically, we use the `MultiSensor_QPE_01H_Pass2` dataset when available and the `GaugeCorr_QPE_01H` for earlier periods.
