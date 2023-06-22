# ERA5 Reanalysis

**ERA5** is a commonly used reanalysis data product.
For more, see

> Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz‐Sabater, J., et al. (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146(730), 1999–2049. <https://doi.org/10.1002/qj.3803>

* For general documentation, see [here](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5)
* For a list of file names used, see see [here](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Table1)

At the moment this repository stores:

* meridional and zonal wind at 500 hPa
* surface air temperature
* elevation (time-invariant, called geopotential)
* vertical integral of meridional and zonal water vapor flux

but it's trivially easy to add more variables by modifying the configuration file (see below)

## Setup

* the domain in time and space is defined in [`era5_config.yml`](./era5_config.yml)
* the conda environment is defined in [`era5_conda.yml`](./era5_conda.yml)
* the Snakemake workflow is defined in [`era5.smk`](./era5.smk)

## Important

You need to have an ECMWF API key.
See [here](https://cds.climate.copernicus.eu/api-how-to).
This is installed on the computer that runs this workflow, but if you are replicating elsewhere you will need to add it yourself.
