"""
Snakefile: see snakemake.readthedocs.io/
"""

from datetime import datetime
import os

from codebase import BoundingBox, TimeRange
from codebase.namingconventions import get_nc_fname, fname2url

# change this variable to save to another location!
# at present I am saving to Rice RDF -- see https://kb.rice.edu/page.php?id=108256#MacOS to access
HOMEDIR = os.path.abspath(".")
DATADIR = os.path.abspath("/Volumes/research/jd82/nexrad-xarray") 

# variables
EXTERNAL = os.path.join(DATADIR, "data", "external")
LOGS = os.path.join(HOMEDIR, "logs")
SCRIPTS = os.path.join(HOMEDIR, "scripts")
PLOTS = os.path.join(HOMEDIR, "plots")
ENVS = os.path.join(HOMEDIR, "envs")

# Define the time range of the analysis
trange = TimeRange(codebase.const.GAUGECORR_BEGINTIME, datetime(2022, 7, 31, 23))

################################################################################
# SNAKEMAKE SETUP
################################################################################

# get netcdf files for each snapshot
netcdf_files = [
    get_nc_fname(dt=dti, dirname=EXTERNAL) for dti in trange.dts
]  # we want to get all of the netcdf files


# default rule
rule default:
    input:
        os.path.join(PLOTS, "demo_plot.png"),


rule demo_plot:
    input:
        files=netcdf_files,
        script=os.path.join(SCRIPTS, "demo_plot.py"),
    output:
        os.path.join(PLOTS, "demo_plot.png"),
    shell:
        "python {input.script} --path {HOMEDIR} --outfile {output}"


################################################################################
# RAW DATA
################################################################################


# this rule convert grib to netcdf
# -r: relative time axis
# -f nc4 specifies output format (netcdf4)
# -z zip_1 specifies zip compression. Empirically small difference between level 1 and level 9
# setctomiss,-3 sets all values of -3 to missing
rule grib2_to_nc:
    input:
        "{fname}.grib2",  # any grib2 file in
    output:
        "{fname}.nc",  # creates a netcdf file
    conda:
        os.path.join(ENVS, "grib2_to_nc.yml")
    shell:
        "cdo -r -f nc4 -z zip_1 setctomiss,-3 -copy {input} {output}"


# creates a (temporarte) grib2 file for each date-time
# the filename is temporary, so the grib2 file is deleted once the netcdf file is created
# first downloads using curl, then unzips using gunzip
rule download_unzip:
    output:
        temp("{fname}.grib2"),
    conda:
        os.path.join(ENVS, "download_unzip.yml")
    params:
        url=lambda wildcards: fname2url(wildcards.fname),
    shell:
        "curl -L {params.url} | gunzip > {output}"
