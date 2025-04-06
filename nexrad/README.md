# NEXRAD Data

**The NOAA NEXRAD radar precipitation data** is very useful for many hydrological applications, but it's stored in a confusing structure on a server hosted by Iowa State.
We use the `MultiSensor_QPE_01H_Pass2` dataset when available and the `GaugeCorr_QPE_01H` for earlier periods.
See below for more information.

The first step of the analysis is to download the `.grib2.gz` file from the Iowa State repository, then unzip the file from `.grib2.gz` to `.grib2`.
This give us a CONUS-scale `grib2` file.

The next step is to define a bounding box for any areas of interest, in [`nexrad_config.yml`](nexrad_config.yml).
Each bounding box has a name and a box of coordinates.
For each bounding box, we extract the data from the grib2 file and save it as a `.nc` file for easier access over a limited study area.
Use these bounding boxes for areas you are actively studying.

## Example usage

```python
import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_mfdataset( # requires dask
    "/Volumes/research/jd82/NEXRAD/Houston_Woodlands_Galveston/2017/08/17/*.nc", # or similar
    concat_dim="time", # specify how to combine the files
    combine="nested",
    decode_timedelta=False, # or else you'll get a warning
)
ds.mean(dim="time")["unknown"].plot()
plt.show()
```

## About this data

There are missing values in the NEXRAD data.
We handle these by skipping them.
If you run into an error with a date you think is missing, please add it to `MISSING_SNAPSHOTS` in [the utility](nexrad_utils/const.py).

### Email 2022-07-07

Hi James,

This is Jian Zhang from NSSL.
I'm the tech lead of the MRMS QPE development and I can probably help with your question.

You are correct that the `MultiSensor_QPE_01H_Pass2` is the most accurate among the MRMS QPE suite.
Since it's not available before mid-Oct 2020, you may use our `GaugeCorr_QPE_01H` product in the early period, which should be very close to the `MultiSensor_QPE_01H_Pass2` in the area of your interest (Gulf Coast).
The `MultiSensor_QPE_01H_Pass2` combines the `GaugeCorr_QPE_01H`, model QPF and precipitation climatology information to help mitigate the deficiency of radar observations (see [this paper](https://doi.org/10.1175/JHM-D-19-0264.1)).
The two products are most different in the complex terrain of western US where there are large radar coverage gaps.
In the southeastern US where the radar and gauge coverage are relatively dense, the `MultiSensor_QPE_01H_Pass2` is largely based on the `GaugeCorr_QPE_01H`.

Best,
Jian
