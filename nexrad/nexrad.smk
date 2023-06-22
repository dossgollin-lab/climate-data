from util.nexrad.nexrad import TimeRange
from util.nexrad.const import GAUGECORR_BEGINTIME, MISSING_SNAPSHOTS
from util.nexrad.namingconventions import get_nc_fname, fname2url


NEXRAD_DATA_DIR = os.path.join(DATADIR, "nexrad")
NEXRAD_SRC_DIR = os.path.join(HOMEDIR, "nexrad")  # this folder


configfile: os.path.join(ERA5_SRC_DIR, "era5_config.yaml")


# this rule convert grib to netcdf
# -r: relative time axis
# -f nc4 specifies output format (netcdf4)
# -z zip_1 specifies zip compression. Empirically small difference between level 1 and level 9
# setctomiss,-3 sets all values of -3 to missing
rule grib2_to_nc:
    input:
        os.path.join(NEXRAD_DATA_DIR, "temp", "{fname}.grib2"),  # any grib2 file in
    output:
        os.path.join(NEXRAD_DATA_DIR, "{fname}.nc"),  # creates a netcdf file
    conda:
        os.path.join(NEXRAD_SRC_DIR, "grib2_to_nc.yml")
    log:
        os.path.join(LOGS, "grib2_to_nc", "{fname}.log"),
    shell:
        "cdo -r -f nc4 -z zip_1 setctomiss,-3 -copy {input} {output}"


# creates a (temporarte) grib2 file for each date-time
# the filename is temporary, so the grib2 file is deleted once the netcdf file is created
# first downloads using curl, then unzips using gunzip
rule download_unzip:
    output:
        temp(os.path.join(NEXRAD_DATA_DIR, "temp", "{fname}.grib2")),
    conda:
        os.path.join(NEXRAD_SRC_DIR, "download_unzip.yml")
    params:
        url=lambda wildcards: fname2url(wildcards.fname),
    log:
        os.path.join(LOGS, "download_unzip", "{fname}.log"),
    shell:
        "curl -L {params.url} | gunzip > {output}"


# a list of all the filenames for which there is data
all_nexrad_nc_files = [
    get_nc_fname(dt=dti, dirname=NEXRAD_DATA_DIR)
    for dti in trange.dts
    if dti not in MISSING_SNAPSHOTS
]


rule nexrad:
    input:
        all_nexrad_nc_files,
