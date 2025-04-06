import os
from datetime import timedelta, datetime
import pandas as pd

# local packages to handle naming conventions
from nexrad_utils.nexrad import TimeRange
from nexrad_utils.const import GAUGECORR_BEGINTIME, MISSING_SNAPSHOTS
from nexrad_utils.namingconventions import get_nc_fname, fname2url, get_grib2_fname

# specify directories to save the data
NEXRAD_DATA_DIR = os.path.join(DATADIR, "NEXRAD")  # final data goes here
NEXRAD_SRC_DIR = os.path.join(HOMEDIR, "nexrad")  # this folder


# Load the nexrad_config.yml file
configfile: os.path.join(NEXRAD_SRC_DIR, "nexrad_config.yml")


# in general, we'll want all available datetimes
current_date = datetime.now().date()
ENDTIME = datetime.combine(
    current_date - timedelta(days=10), datetime.min.time()
) + timedelta(hours=23)
trange = TimeRange(GAUGECORR_BEGINTIME, ENDTIME)

# for demonstration purposes, we run just August 17, 2017
t0 = datetime(2017, 8, 17, 0)
t1 = datetime(2017, 8, 17, 23)
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

# Access bounding_boxes from the loaded configuration
bounding_boxes = config["bounding_boxes"]

# Define the NetCDF4 output files for each bounding box and GRIB2 file combination
all_nexrad_nc_files = [
    get_nc_fname(dt, dirname=NEXRAD_DATA_DIR, bbox_name=bbox["name"])
    for dt in t_nonmissing
    for bbox in bounding_boxes
]


rule grib2_to_netcdf4:
    input:
        script=os.path.join(NEXRAD_SRC_DIR, "grib2_to_netcdf4.py"),
        grib2_file=os.path.join(
            NEXRAD_DATA_DIR, "{year}", "{month}", "{day}", "{fname}.grib2"
        ),
    output:
        nc_file=os.path.join(
            NEXRAD_DATA_DIR, "{bbox_name}", "{year}", "{month}", "{day}", "{fname}.nc"
        ),
    params:
        lon_min=lambda wildcards: next(
            bbox["lon_min"]
            for bbox in config["bounding_boxes"]
            if bbox["name"] == wildcards.bbox_name
        ),
        lon_max=lambda wildcards: next(
            bbox["lon_max"]
            for bbox in config["bounding_boxes"]
            if bbox["name"] == wildcards.bbox_name
        ),
        lat_min=lambda wildcards: next(
            bbox["lat_min"]
            for bbox in config["bounding_boxes"]
            if bbox["name"] == wildcards.bbox_name
        ),
        lat_max=lambda wildcards: next(
            bbox["lat_max"]
            for bbox in config["bounding_boxes"]
            if bbox["name"] == wildcards.bbox_name
        ),
    conda:
        os.path.join(NEXRAD_SRC_DIR, "grib2_to_netcdf4.yml")
    shell:
        "python {input.script} --input {input.grib2_file} --output {output.nc_file} --lonmin {params.lon_min} --lonmax {params.lon_max} --latmin {params.lat_min} --latmax {params.lat_max}"


rule clean_nexrad:
    shell:
        f"rm -f {NEXRAD_DATA_DIR}/*/*/*/*.idx"


rule nexrad:
    input:
        all_nexrad_grib2_files,
        all_nexrad_nc_files,
