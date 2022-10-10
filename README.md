# Doss-Gollin Lab Climate Data Repository

This is a **work in progress**!
Use this software **with caution**!
If you find it helpful please consider using the `Issues` tab to identify problems or suggest improvements (there are already several things there)!

## Overview

This repository contains code needed to access weather and climate data commonly re-used in the Doss-Gollin lab.
None of the actual data is contained in this repository!
Instead, it is downloaded from various external sources and then stored on the Rice Research Data Facility.
Use of this facility is not free, so we should only store the datasets that we expect to use frequently.
If you have questions, contact James.

All data is stored as NetCDF4 files for easy use with the user-friendly, accessible, and standard [Pangeo](https://pangeo.io/) ecosystem.

## Accessing the data

You don't need to use the codes in this repository to access the data.
The data is stored on James's RDF account.
See the lab manual on Notion for details of accessing the data.

### Datasets included

**The NOAA NEXRAD radar precipitation data** is very useful for many hydrological applications, but it's stored in a confusing structure on a server hosted by Iowa State.
This makes it hard to use with the user-friendly, accessible, and standard [Pangeo](https://pangeo.io/) ecosystem.
We use the `MultiSensor_QPE_01H_Pass2` dataset when available and the `GaugeCorr_QPE_01H` for earlier periods.
See [docs](./doc/) for more information.
The basic steps of the analysis are

1. Download the `.grib2.gz` file from the Iowa State repository
1. Unzip the file from `.grib2.gz` to `.grib2`
1. Use the `cdo` tool to convert from `.grib2` to NetCDF 4 (`.nc`)
1. Leverage the `open_mfdataset` functionality in `xarray` to handle datasets spread across many files

**ERA5** is a commonly used reanalysis data product.
At the moment this repository stores:

- meridional and zonal wind at 500 hPa
- surface air temperature
- elevation (time-invariant, called geopotential)
- vertical integral of meridional and zonal water vapor flux

from 2015-2022.
Adding additional years would be straightforward; edit 

## Developing this dataset

If you want to change the files we track or edit this repository, then this section is for you.
This repository uses [Snakemake](https://snakemake.readthedocs.io/) to define and specify dependencies and workflows.
If you've never used Snakemake before, you should read up on it.

We also use Anaconda to manage dependencies.
This includes using Anaconda to specify the dependencies for each workflow rule, making the workflow more concise and reproducible.

If you run into problems please use the `Issues` tab on GitHub to bring them to our attention.

### Installation

You will need [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed.
Then open a terminal and run the following lines

```shell
conda env create --file environment.yml # creates the environment
conda activate nexrad # activates the environment
pip install -e . # install the local package in codebase/
```

All other required dependencies are described using Snakemake and anaconda environments (see [Snakemake docs](https://snakemake.readthedocs.io/)).

### Adjust the path

The location where data will be stored is defined in `config.yaml` under the `datadir` argument.
This should point to the location where the RDF is mounted.
To mount the RDF locally, follow the directions [here](https://kb.rice.edu/page.php?id=108256).
If you follow the default settings, you shouldn't need to adjust the path specified in `config.yaml`.

If you are mounting on Linux, be aware that you need to change the `uid` argument.
For example the command

```shell
sudo mount.cifs -o username=jd82,domain=ADRICE,mfsymlinks,rw,vers=3.0,sign,uid=jd82 //smb.rdf.rice.edu/research $HOME/RDF
```

will mount the RDF to `$HOME/RDF` for user `jd82`.
If you copy and paste, be aware that this documentation doesn't make very clear that you need to change the `uid`.

### Running codes

To update the entire dataset, run something like

```shell
snakemake  --use-conda --cores SOME_NUMBER
```

where `SOME_NUMBER` is the number of cores you want to use (e.g., `--cores all`).
There are many additional arguments you can pass -- see [Snakemake docs](https://snakemake.readthedocs.io/).

### Prototyping

It takes Snakemake a long time to build the DAG.
When you're just rapidly prototyping things, this lag time is annoying.
To speed up, you can batch files like this:

```shell
snakemake nexrad --use-conda --cores 1 --batch nexrad=1/1000
```

See [dealing with very large workflows](https://snakemake.readthedocs.io/en/stable/executing/cli.html#dealing-with-very-large-workflows) for more details.


### Sensible default

If you just want to build the dataset, a good default command to use is

```shell
snakemake --use-conda --cores all  --rerun-incomplete --keep-going
```

Note:

- `use_conda`: use anaconda for environments
- `--cores 10`: use 10 cores (out of 12)
- `--rerun-incomplete`: reduces errors if a job was canceled earlier
- `--keep-going`: if a file causes an error, don't give up

If you are on a different machine you can learn about how many cores are available with the `lscpu` command.

If you are running on a remote machine via `ssh`, then prepending the command above with [`nohup`](https://www.computerhope.com/unix/unohup.htm) may be a good idea.
In a nutshell, this will keep the process running even after you close your `ssh` session.

### Linters

Linters should run automatically if you are using VS Code with relevant extensions installed.
Before submitting a pull request, please `activate nexrad` and then

- `snakefmt .` to reformat the Snakefile
- `black .` to reformat the code
- `mypy . --ignore-missing-imports` to run type checks on the code. This is a good way to catch bugs.

Additionally, if you're messing with `Snakefile` then `snakemake --lint` is a helpful resource with good suggestions.

We are working to get these to run automatically using GitHub workflows.
See [this issue](https://github.com/dossgollin-lab/nexrad-xarray/issues/5) and help out if you're goot at GitHub Actions.
