# NEXRAD-xarray

This program will create a database of NEXRAD radar precipitation data in formats that are easy to use for analysis.
Conceptually, the steps are:

1. Download the raw data. The raw data is zipped on Iowa State's servers, with one `.grib2` file corresponding to one time step ("snapshot") and store the unzipped raw data to file. It is highly compressed, so it doesn't take up too much space. This data lives in `./data/grib2/`
1. Use `xarray` to read in each `.grib2` file and save a spatial subset of it as a netcdf4 file. Although these files are less compressed, they are faster to read in.
1. Use `xarray`'s `open_mfdataset`, which leverages the power of `dask` for lazy loading, to read in all the data from netcdf4 files, subset, and extract the information of interest. See `demo.ipynb` for a simple demo

The main tool used to accomplish this is [Snakemake](snakemake.readthedocs.io/), which is a reproducible workflow management system that is deeply integrated with Python.

## Installation

You need to have a recent version of python.
The following instructions use `mamba`, which is a slightly faster and fancier version of `conda`.
You can replace `mamba` with `conda` if you would like.

```shell
mamba env create --file environment.yml # can use conda instead of mamba
conda activate nexrad # activate environment
pip install -e . # install local package
```

## To run

Once you have installed,

```shell
snakemake --cores <n_cores>
```

where `<n_cores>` is the number of cores you want to use.
1 is a safe default if you don't want to multithread, but it this will take a while -- reading in each `.grib2` file takes on the order of 10 seconds, and there is a file for each hour.

If you want to change the spatial domain retained as a `.nc` file, edit `config.yml`.
If you want to change the time domain, edit `Snakefile`.

## To do

This is a work in progress!

- [ ] Verify the correct variable to use. This may be time dependent.
- [ ] Get this up and running on Rice RDF Isilon
