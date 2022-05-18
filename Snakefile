"""
Snakefile: see snakemake.readthedocs.io/
We use Snakefile to collect and process required data.
"""

configfile: "config.yml"

from datetime import datetime

import pandas as pd
import xarray as xr

from codebase import nexrad
from codebase.path import datadir, scriptdir

T_START = datetime(2022, 4, 15, 0)  # the first time to collect
T_END = datetime(2022, 4, 19, 23)  # the last time to collect

# a table of all the raw files and filenames
snapshots = pd.DataFrame({"datetime": pd.date_range(T_START, T_END, freq="H")}).assign(
    url=lambda df: [nexrad.get_url(dt) for dt in df.datetime],
    local=lambda df: [datadir("grib2", nexrad.grib2_fname(dt)) for dt in df.datetime],
    local_nc=lambda df: [
        datadir("nc", nexrad.grib2_fname(dt).replace(".grib2", ".nc"))
        for dt in df.datetime
    ],
)


# this rule tells Snakemake to create all the data that is imported directly into the Jupyter notebooks
rule default_rule:
    input:
        expand("{file}", file=snapshots.local_nc),


# this rule downloads and unzips a raw grib file
rule download_grib2:
    output:
        datadir("grib2", "{fname}"),
    params:
        url=lambda wildcards: snapshots.loc[
            lambda df: df["local"] == datadir("grib2", wildcards.fname)
        ].url.values[0],
    shell:
        "curl -L {params.url} | gunzip > {output}"


# this rule creates a netcdf4 file for each snapshot over a reduced region
rule build_netcdf:
    input:
        file=datadir("grib2", "{fname}.grib2"),
        script=scriptdir("grib_to_nc.py"),
    params:
        lonmin=config["limits"]["lonmin"],
        lonmax=config["limits"]["lonmax"],
        latmin=config["limits"]["latmin"],
        latmax=config["limits"]["latmax"],
    output:
        datadir("nc", "{fname}.nc"),
    shell: "python {input.script} --infile {input.file} --outfile {output} --lonmin {params.lonmin} --lonmax {params.lonmax} --latmin {params.latmin} --latmax {params.latmax}"