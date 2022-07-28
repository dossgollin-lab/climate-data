"""
Snakefile: see snakemake.readthedocs.io/
"""

from datetime import datetime
import os

from codebase import BoundingBox, TimeRange
from codebase.namingconventions import get_url, get_gz_fname, get_grib2_fname, get_nc_fname, fname2url
from codebase.util import download_file

# Define the bounding box of the analysis
bbox = BoundingBox(
    lonmin=260,
    lonmax=290,
    latmin=25,
    latmax=40,
)

# Define the time range of the analysis
trange = TimeRange(
    stime=datetime(2017, 8, 1, 0), etime=datetime(2017, 8, 31, 23)
)

################################################################################
# SNAKEMAKE SETUP
################################################################################

# this rule tells Snakemake to create all the data that is imported directly into the Jupyter notebooks
rule default_rule:
    input:
        [get_nc_fname(dt=dti, dirname="data/external") for dti in trange.dts] # we want to get all of the netcdf files


################################################################################
# RAW DATA
################################################################################

# this rule creates a netcdf4 file for each snapshot over a reduced region
# the `cdo` command will convert to netcdf, replace -3 with missing, and use level 1 compression
rule grib2_to_nc:
    input: "{fname}.grib2"
    output: "{fname}.nc"
    shell: "cdo -f nc4 -z zip_1 setctomiss,-3 -copy {input} {output}"

# creates a (temporarte) grib2 file for each date-time
# this temporary file is deleted once all downstream steps are complete
rule download_unzip:
    output: temp("{fname}.grib2")
    params:
        url=lambda wildcards: fname2url(wildcards.fname)
    shell:
        "curl -L {params.url} | gunzip > {output}"
