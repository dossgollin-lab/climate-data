# NEXRAD-xarray

This is a **work in progress**!
Use this software **with caution**!
If you find it helpful please consider using the `Issues` tab to identify problems or suggest improvements.

This program will create a database of NEXRAD radar precipitation data in formats that are easy to use for analysis, specifically Netcdf4 files that play nicely with the [Pangeo](https://pangeo.io/) ecosystem and can be stored on a local hard drive.
Conceptually, the steps are:

1. Download the raw data. The raw data is stored in compressed format on Iowa State's servers, with one `.grib2` file corresponding to one time step ("snapshot", i.e. one hour). Once the data is downloaded, it is decompressed it is stored in `./data/grib2/`. This data format is relatively compressed, so each file is of order 500kB.
1. Use `xarray` to read in each `.grib2` file and save a spatial subset of it (set the boundaries in `config.yml`) as a netcdf4 file. Although these files are less compressed, they are much faster to read in. This step is rather slow because it takes a while (~10 seconds per snapshot) for `xarray` to parse the `.grib2` files correctly.
1. Use `xarray`'s `open_mfdataset`, which leverages the power of `dask` for lazy loading, to read in all the data from netcdf4 files, subset, and extract the spatial/temporal boundaries of interest. See `demo.ipynb` for a simple demo

The main tool used to accomplish this is [Snakemake](snakemake.readthedocs.io/), which is a reproducible workflow management system that is deeply integrated with Python.

## Installation

Installation assumes that you are using Anaconda.
It should in principle be possible to use other Python package managers, but we haven't tried.
The following instructions actually use `mamba`, which is a slightly faster and fancier version of `conda`; you can replace `mamba` with `conda` if you prefer.

In your terminal:

```shell
mamba env create --file environment.yml # can use conda instead of mamba
conda activate nexrad # activate environment
pip install -e . # install local package
```

## To run

Once you have installed,

```shell
conda activate nexrad # make sure it's activated
snakemake --cores <n_cores>
```

where `<n_cores>` is the number of cores you want to use.
1 is a safe default if you don't want to multithread, but it this will take a while -- reading in each `.grib2` file takes on the order of 10 seconds, and there is a file for each hour.

If you want to change the spatial domain retained as a `.nc` file, edit `config.yml`.
If you want to change the time domain, edit the `Snakefile`.
