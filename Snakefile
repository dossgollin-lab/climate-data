"""
Snakefile: see snakemake.readthedocs.io/
"""

from datetime import datetime
import platform
import os

from codebase import TimeRange
from codebase.const import GAUGECORR_BEGINTIME, MISSING_SNAPSHOTS
from codebase.namingconventions import get_nc_fname, fname2url

################################################################################
# CONSTANTS AND CONFIGURABLE OPTIONS
################################################################################

# Define the time range of the analysis
trange = TimeRange(GAUGECORR_BEGINTIME, datetime(2022, 7, 31, 23))

################################################################################
# CONFIGURE DATA / FILE STORAGE LOCATIONS
################################################################################


configfile: "config.yaml"


HOMEDIR = os.path.abspath(".")  # most stuff should be stored locally

# store the data on a remote location
# at present I am saving to Rice RDF -- see https://kb.rice.edu/page.php?id=108256
system = platform.system()
if system == "Darwin":
    DATADIR = os.path.abspath(config["datadir"]["osx"])
elif system == "Linux":
    DATADIR = os.path.abspath(config["datadir"]["linux"])
elif system == "Windows":
    DATADIR = os.path.abspath(config["datadir"]["windows"])
else:
    raise ValueError("Unsupported platform")

# we can use these paths as variables below
EXTERNAL = os.path.join(DATADIR, "data", "external")
SCRIPTS = os.path.join(HOMEDIR, "scripts")
PLOTS = os.path.join(HOMEDIR, "plots")
ENVS = os.path.join(HOMEDIR, "envs")

################################################################################
# NEXRAD DATA
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


# a list of all the filenames for which there is data
all_nexrad_nc_files = [
    get_nc_fname(dt=dti, dirname=EXTERNAL)
    for dti in trange.dts
    if dti not in MISSING_SNAPSHOTS
]


rule nexrad:
    input:
        all_nexrad_nc_files,


################################################################################
# REANALYSIS
################################################################################


# 0.1 degree elevation data
# see https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation#ERA5Land:datadocumentation-parameterlistingParameterlistings
elevation_fname = os.path.join(EXTERNAL, "reanalysis", "elevation.nc")
elevation_url = "https://confluence.ecmwf.int/download/attachments/140385202/geo_1279l4_0.1x0.1.grib2_v4_unpack.nc?version=1&modificationDate=1591979822003&api=v2"


rule download_elevation:
    output:
        elevation_fname,
    conda:
        os.path.join(ENVS, "download_unzip.yml")  # just needs curl
    params:
        url=elevation_url,
    shell:
        "curl -L {params.url}  > {output}"


all_reanalysis_files = [elevation_fname]


rule reanalysis:
    input:
        all_reanalysis_files,


################################################################################
# DEFAULT RULE
################################################################################


# default rule runs everything
rule default:
    input:
        all_nexrad_nc_files,
        all_reanalysis_files,
