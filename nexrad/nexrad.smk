import os
from datetime import timedelta, datetime
import pandas as pd

# Use our local package
from util.nexrad.nexrad import TimeRange
from util.nexrad.const import GAUGECORR_BEGINTIME, MISSING_SNAPSHOTS
from util.nexrad.namingconventions import get_nc_fname, fname2url

# Define directories
NEXRAD_DATA_DIR = os.path.join(DATADIR, "NEXRAD")
NEXRAD_SRC_DIR = os.path.join(HOMEDIR, "nexrad")  # this folder

# Keep temporary files local because I/O to RDF is super slow
NEXRAD_TEMP_DIR = "~/Downloads/NEXRAD/temp"


# Define the configuration file
# configfile: os.path.join(NEXRAD_SRC_DIR, "nexrad_config.yaml")

# Define the time range to access
ENDTIME = datetime(2023, 9, 30, 23)
trange = TimeRange(GAUGECORR_BEGINTIME, ENDTIME)
t_nonmissing = [t for t in trange.dts if t not in MISSING_SNAPSHOTS]


# creates a (temporary) grib2 file for each date-time
# the filename is temporary, so the grib2 file is deleted once the netcdf file is created
# first downloads using curl, then unzips using gunzip
rule download_unzip:
    output:
        temp(os.path.join(NEXRAD_TEMP_DIR, "{fname}.grib2")),
    conda:
        os.path.join(NEXRAD_SRC_DIR, "download_unzip.yml")
    params:
        url=lambda wildcards: fname2url(wildcards.fname),
    log:
        os.path.join(LOGS, "download_unzip", "{fname}.log"),
    shell:
        "curl -L {params.url} | gunzip > {output}"


# this rule convert grib to netcdf
# -r: relative time axis
# -f nc4 specifies output format (netcdf4)
# -z zip_1 specifies zip compression. Empirically small difference between level 1 and level 9
# setctomiss,-3 sets all values of -3 to missing
rule grib2_to_nc:
    input:
        os.path.join(NEXRAD_TEMP_DIR, "{fname}.grib2"),
    output:
        temp(os.path.join(NEXRAD_TEMP_DIR, "{fname}.nc")),
    conda:
        os.path.join(NEXRAD_SRC_DIR, "grib2_to_nc.yml")
    log:
        os.path.join(LOGS, "grib2_to_nc", "{fname}.log"),
    shell:
        "cdo -r -f nc4 -z zip_1 setctomiss,-3 -copy {input} {output}"


# Rule to combine all 1-hour files from an entire year into a single file
rule combine_files:
    input:
        files=lambda wildcards: [
            os.path.join(NEXRAD_TEMP_DIR, get_nc_fname(dt))
            for dt in t_nonmissing
            if dt.year == int(wildcards.year)
        ],
        script=os.path.join(NEXRAD_SRC_DIR, "combine_files.py"),
    output:
        os.path.join(NEXRAD_DATA_DIR, "{year}.nc"),
    conda:
        os.path.join(NEXRAD_SRC_DIR, "combine_files.yml")
    shell:
        "python {input.script} {' '.join(input.files)} {output}"


# a list of all the filenames for which there is data
years = set([dt.year for dt in trange.dts])
all_nexrad_nc_files = [os.path.join(NEXRAD_DATA_DIR, f"{year}.nc") for year in years]


rule nexrad:
    input:
        all_nexrad_nc_files,
