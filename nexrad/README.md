# NEXRAD Data

**The NOAA NEXRAD radar precipitation data** is very useful for many hydrological applications, but it's stored in a confusing structure on a server hosted by Iowa State.
We use the `MultiSensor_QPE_01H_Pass2` dataset when available and the `GaugeCorr_QPE_01H` for earlier periods.
See [docs](./doc/) for more information.
The basic steps of the analysis are

1. Download the `.grib2.gz` file from the Iowa State repository
1. Unzip the file from `.grib2.gz` to `.grib2`
1. Use the `cdo` tool to convert from `.grib2` to NetCDF 4 (`.nc`)

## About this data

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
