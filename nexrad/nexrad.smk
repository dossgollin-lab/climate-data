import os
from datetime import timedelta, datetime
import pandas as pd

# Use our local package
from util.nexrad.nexrad import TimeRange
from util.nexrad.const import GAUGECORR_BEGINTIME, MISSING_SNAPSHOTS
from util.nexrad.namingconventions import get_nc_fname, fname2url, get_grib2_fname

# Define directories
NEXRAD_DATA_DIR = os.path.join(DATADIR, "NEXRAD")
NEXRAD_SRC_DIR = os.path.join(HOMEDIR, "nexrad")  # this folder
NEXRAD_TEMP_DIR = os.path.join(HOMEDIR, "temp", "nexrad") # a temp folder

# Define the time range to access
current_date = datetime.now().date()
ENDTIME = datetime.combine(current_date - timedelta(days=10), datetime.min.time()) + timedelta(hours=23)
#trange = TimeRange(GAUGECORR_BEGINTIME, ENDTIME)
t0 = datetime(2017, 8, 1, 0)
t1 = datetime(2017, 8, 31, 23)
trange = TimeRange(t0, t1)
t_nonmissing = [t for t in trange.dt_valid if t not in MISSING_SNAPSHOTS]


# creates a (temporary) grib2 file for each date-time
# the filename is temporary, so the grib2 file is deleted once the netcdf file is created
# first downloads using curl, then unzips using gunzip
rule download_unzip:
    output:
        os.path.join(NEXRAD_DATA_DIR, "{fname}.grib2"),
    conda:
        os.path.join(NEXRAD_SRC_DIR, "download_unzip.yml")
    params:
        url=lambda wildcards: fname2url(wildcards.fname),
    log:
        os.path.join(LOGS, "download_unzip", "{fname}.log"),
    shell:
        "curl -L {params.url} | gunzip > {output}"



# a list of all the filenames for which there is data
all_nexrad_grib2_files = [
    get_grib2_fname(dt, dirname=NEXRAD_DATA_DIR) for dt in t_nonmissing
]

rule nexrad:
    input:
        all_nexrad_grib2_files,
