# NEXRAD-xarray

This is a **work in progress**!
Use this software **with caution**!
If you find it helpful please consider using the `Issues` tab to identify problems or suggest improvements (there are already several things there).

## Overview

The NOAA NEXRAD radar precipitation data is very useful for many hydrological applications, but it's stored in a confusing structure on a server hosted by Iowa State.
This makes it hard to use with the user-friendly, accessible, and standard [Pangeo](https://pangeo.io/) ecosystem.

### About: data variables

We use the `MultiSensor_QPE_01H_Pass2` dataset when available and the `GaugeCorr_QPE_01H` for earlier periods.
See [docs](./doc/) for more information.

The basic steps of the analysis are

1. Download the `.grib2.gz` file from the Iowa State repository
1. Unzip the file from `.grib2.gz` to `.grib2`
1. Use the `cdo` tool to convert from `.grib2` to NetCDF 4 (`.nc`)
1. Leverage the `open_mfdataset` functionality in `xarray` to handle datasets spread across many files

### Approach

We use three main tools.

1. [Snakemake](https://snakemake.readthedocs.io/) is a powerful tool for specifying dependencies and workflows.
1. The [Climate Data Operators](https://code.mpimet.mpg.de/projects/cdo) program to convert from `.grib2` to NetCDF4 files quickly and efficiently.
1. Anaconda (mainly python) to manage dependencies.

Some familiarity with these tools will be helpful if you want to edit our codes, but you can run them with only a passing knowledge of the linux shell and the ability to make very basic changes to [Snakefile](./Snakefile) (which is essentially python).

## To run our codes

If you run into problems please use `Issues` tab on GitHub to bring them to our attention.

### Installation

You will need [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed.
Then open a terminal and run the following lines\

```shell
conda env create --file environment.yml # creates the environment
conda activate nexrad # activates the environment
pip install -e . # install the local package in codebase/
```

All other required dependencies are described using Snakemake and anaconda environments (see [Snakemake docs](https://snakemake.readthedocs.io/)).

### Change the path

Edit the **CONFIGURE DATA / FILE STORAGE LOCATIONS** section of [`Snakefile`](./Snakefile) and change the `DATADIR` to suit your needs.
We have currently configured it to save the data to the Rice RDF mounted locally -- see To mount RDF on Linux, follow the directions [here](https://kb.rice.edu/page.php?id=108256).
(Windows access is possible but not yet supported -- please open a PR!)

### Quick version

```shell
snakemake  --use-conda --cores SOME_NUMBER
```

where `SOME_NUMBER` is the number of cores you want to use (e.g., `--cores 2`).
There are many additional arguments you can pass -- see [Snakemake docs](https://snakemake.readthedocs.io/).

## Technical details

This is a bit of living documentation.
For now it is badly organized :).

### Approximate storage requirements

One snapshot takes up approximately 3MB; one month requires about 2.55GB.

### Prototyping

It takes Snakemake a long time to build the DAG.
When you're just rapidly prototyping things, this lag time is annoying.
To speed up, you can batch files like this:

```shell
snakemake netcdf_files --use-conda --cores 1 --batch netcdf_files=1/1000
```

See [dealing with very large workflows](https://snakemake.readthedocs.io/en/stable/executing/cli.html#dealing-with-very-large-workflows) for more details.

### File system stuff

To mount RDF on Linux, follow the directions [here](https://kb.rice.edu/page.php?id=108256#Linux).
Be aware that you need to change the `uid` argument.

For example the command

```shell
sudo mount.cifs -o username=jd82,domain=ADRICE,mfsymlinks,rw,vers=3.0,sign,uid=jd82 //smb.rdf.rice.edu/research $HOME/RDF
```

will mount the RDF to `$HOME/RDF` for user `jd82`.
If you copy and paste, be aware that this documentation doesn't make very clear that you need to change the `uid`.

### A good command on our group workstation

If you just want to build the dataset, a good default command to use is

```shell
snakemake --use-conda --cores all  --rerun-incomplete --keep-going netcdf_files
```

Note:

- `use_conda`: use anaconda for environments
- `--cores 10`: use 10 cores (out of 12)
- `--rerun-incomplete`: reduces errors if a job was canceled earlier
- `--keep-going`: if a file causes an error, don't give up

If you are on a different machine you can learn about how many cores are available with the `lscpu` command.
