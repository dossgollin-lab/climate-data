# Doss-Gollin Lab Climate Data Repository

This is a **work in progress**!
Use this software **with caution**!
If you find it helpful please usie the `Issues` tab to identify problems or suggest improvements (there are already several things there)!

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

Our philosophy is to avoid storing too much data on a single file.
To deal with datasets spread across many files, we suggest to leverage the `open_mfdataset` functionality in `xarray`.

### What Datasets are Included?

1. Radar precipitation data over the continental United States. For more details, see [the README](./nexrad/README.md).
1. ERA5 reanalysis data over the continental United States at 0.25 degree resolution. For more details, see [the README](./era5/README.md). Specifically, we have the following variables:
    * meridional and zonal wind at 500 hPa
    * surface air temperature
    * elevation (time-invariant, called geopotential)
    * vertical integral of meridional and zonal water vapor flux

## Developing this dataset

If you want to change the files we track or edit this repository, then this section is for you.
This repository uses [Snakemake](https://snakemake.readthedocs.io/) to define and specify dependencies and workflows.
If you've never used Snakemake before, you should read up on it.

We also use conda to manage dependencies.
This includes using conda to specify the dependencies for each workflow rule, making the workflow more concise and reproducible.
If you run into problems please use the `Issues` tab on GitHub to bring them to our attention.

### Installation

You will need [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed (or [`mamba`](https://anaconda.org/conda-forge/mamba) for maximum performance).
Then open a terminal and run the following lines

```shell
conda env create --file environment.yml # creates the environment
conda activate climatedata # activates the environment
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
You can find this with the `id` command.

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
nohup snakemake /home/jd82/RDF/jd82/NEXRAD/2020-11.nc --use-conda --cores all --rerun-incomplete &
```

See [dealing with very large workflows](https://snakemake.readthedocs.io/en/stable/executing/cli.html#dealing-with-very-large-workflows) for more details.

### Sensible default

If you just want to build the dataset, a good default command to use is

```shell
nohup snakemake all --use-conda --cores all  --rerun-incomplete --keep-going
```

Note:

* `nohup`: Keep running on a remote machine via `ssh`, even if the connection closes (see [`nohup`](https://www.computerhope.com/unix/unohup.htm) docs).
* `use_conda`: use anaconda for environments
* `--cores all`: use all cores (workstation has 12)
* `--rerun-incomplete`: reduces errors if a job was canceled earlier
* `--keep-going`: if a file causes an error, don't give up

If you are on a different machine you can learn about how many cores are available with the `lscpu` command.

In a nutshell, this will keep the process running even after you close your `ssh` session.

### Linters

Linters should run automatically if you are using VS Code with relevant extensions installed.
Before submitting a pull request, please `activate nexrad` and then

* `snakefmt .` to reformat the Snakefile
* `black .` to reformat the code
* `mypy . --ignore-missing-imports` to run type checks on the code. This is a good way to catch bugs.

Additionally, if you're messing with `Snakefile` then `snakemake --lint` is a helpful resource with good suggestions.

We are working to get these to run automatically using GitHub workflows.
See [this issue](https://github.com/dossgollin-lab/nexrad-xarray/issues/5) and help out if you're goot at GitHub Actions.

### Pro tips

I am terrible at shell stuff so here are some handy commands

After running Snakemake, you may get some time steps that throw an error.
Snakemake will generate a log file for you with something that looks like

```shell
Complete log: .snakemake/log/2022-10-11T071442.418042.snakemake.log
```

To parse this log file to get all the dates that threw errors, something like this will work:

```shell
grep "output:" PATH_TO_LOG_FILE | cut -c69- | sort | uniq > lines.log
```
