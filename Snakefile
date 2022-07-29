"""
Snakefile: see snakemake.readthedocs.io/
"""

from datetime import datetime
import os

from codebase import BoundingBox, TimeRange
from codebase.namingconventions import get_nc_fname, fname2url

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

# get netcdf files for each snapshot
netcdf_files = [get_nc_fname(dt=dti, dirname="data/external") for dti in trange.dts] # we want to get all of the netcdf files

# default rule
rule default:
    input: netcdf_files
    output: "plots/demo_map.png"
    script: "scripts/demo.py"



################################################################################
# RAW DATA
################################################################################

# this rule convert grib to netcdf
# -r: relative time axis
# -f nc4 specifies output format (netcdf4)
# -z zip_1 specifies zip compression. Empirically small difference between level 1 and level 9
# setctomiss,-3 sets all values of -3 to missing
rule grib2_to_nc:
    input: "{fname}.grib2" # any grib2 file in
    output: "{fname}.nc" # creates a netcdf file
    log: "logs/grib2_to_nc/{fname}.log"
    conda: "envs/grib2_to_nc.yml" # use a specific environment
    shell: "cdo -r -f nc4 -z zip_1 setctomiss,-3 -copy {input} {output}"

# creates a (temporarte) grib2 file for each date-time
# the filename is temporary, so the grib2 file is deleted once the netcdf file is created
# first downloads using curl, then unzips using gunzip
rule download_unzip:
    output: temp("{fname}.grib2")
    conda: "envs/download_unzip.yml" # use a specific environment
    log: "logs/download_unzip/{fname}.log"
    params:
        url=lambda wildcards: fname2url(wildcards.fname)
    shell: "curl -L {params.url} | gunzip > {output}"
