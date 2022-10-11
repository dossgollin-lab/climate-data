"""
Snakefile: see snakemake.readthedocs.io/
"""

from datetime import datetime
import platform
import os

from nexrad import TimeRange
from nexrad.const import GAUGECORR_BEGINTIME, MISSING_SNAPSHOTS
from nexrad.namingconventions import get_nc_fname, fname2url

################################################################################
# CONSTANTS AND CONFIGURABLE OPTIONS
################################################################################

# Define the time range of the analysis
trange = TimeRange(GAUGECORR_BEGINTIME, datetime(2021, 12, 31, 23))

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
SCRIPTS = os.path.join(HOMEDIR, "scripts")
PLOTS = os.path.join(HOMEDIR, "plots")
ENVS = os.path.join(HOMEDIR, "envs")
LOGS = os.path.join(HOMEDIR, "logs")

################################################################################
# NEXRAD DATA
################################################################################

NEXRAD = os.path.join(DATADIR, "nexrad")


# this rule convert grib to netcdf
# -r: relative time axis
# -f nc4 specifies output format (netcdf4)
# -z zip_1 specifies zip compression. Empirically small difference between level 1 and level 9
# setctomiss,-3 sets all values of -3 to missing
rule grib2_to_nc:
    input:
        os.path.join(NEXRAD, "temp", "{fname}.grib2"),  # any grib2 file in
    output:
        os.path.join(NEXRAD, "{fname}.nc"),  # creates a netcdf file
    conda:
        os.path.join(ENVS, "grib2_to_nc.yml")
    log:
        os.path.join(LOGS, "grib2_to_nc", "{fname}.log"),
    shell:
        "cdo -r -f nc4 -z zip_1 setctomiss,-3 -copy {input} {output}"


# creates a (temporarte) grib2 file for each date-time
# the filename is temporary, so the grib2 file is deleted once the netcdf file is created
# first downloads using curl, then unzips using gunzip
rule download_unzip:
    output:
        temp(os.path.join(NEXRAD, "temp", "{fname}.grib2")),
    conda:
        os.path.join(ENVS, "download_unzip.yml")
    params:
        url=lambda wildcards: fname2url(wildcards.fname),
    log:
        os.path.join(LOGS, "download_unzip", "{fname}.log"),
    shell:
        "curl -L {params.url} | gunzip > {output}"
        

# a list of all the filenames for which there is data
all_nexrad_nc_files = [
    get_nc_fname(dt=dti, dirname=NEXRAD)
    for dti in trange.dts
    if dti not in MISSING_SNAPSHOTS
]


rule nexrad:
    input:
        all_nexrad_nc_files,


################################################################################
# REANALYSIS
################################################################################

REANALYSIS = os.path.join(DATADIR, "ERA5")

# some strings to reuse
str_resolution = " --resolution {}".format(config["era5_resolution"])
str_bounds = " --lonmin {} --lonmax {} --latmin {} --latmax {}".format(
    config["bounds"]["lonmin"],
    config["bounds"]["lonmax"],
    config["bounds"]["latmin"],
    config["bounds"]["latmax"],
)


elevation_fname = os.path.join(REANALYSIS, "single_level", "elevation.nc")


rule era5_elevation:
    input:
        os.path.join(SCRIPTS, "download_era5_orography.py"),
    output:
        elevation_fname,
    log:
        os.path.join(LOGS, "era5_elevation.log"),
    conda:
        os.path.join(ENVS, "era5.yml")
    shell:
        "python {input} --outfile {output}" + str_resolution + str_bounds


rule era5_pressure:
    input:
        os.path.join(SCRIPTS, "download_era5_pressure.py"),
    output:
        os.path.join(REANALYSIS, "pressure_level", "{variable}_{pressure}_{year}.nc"),
    log:
        os.path.join(LOGS, "era5_pressure", "{variable}_{pressure}_{year}.log"),
    conda:
        os.path.join(ENVS, "era5.yml")
    shell:
        (
            "python {input} --outfile {output} --variable {wildcards.variable} --pressure {wildcards.pressure} --year {wildcards.year}"
            + str_resolution
            + str_bounds
        )


rule era5_single_level:
    input:
        os.path.join(SCRIPTS, "download_era5_single_level.py"),
    output:
        os.path.join(REANALYSIS, "single_level", "{variable}_{year}.nc"),
    log:
        os.path.join(LOGS, "era5_single_level", "{variable}_{year}.log"),
    conda:
        os.path.join(ENVS, "era5.yml")
    shell:
        (
            "python {input} --outfile {output} --variable {wildcards.variable} --year {wildcards.year}"
            + str_resolution
            + str_bounds
        )


era5_years = range(config["era5_years"]["first"], config["era5_years"]["last"] + 1)

# see https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Table1
uwnd_files = [
    os.path.join(REANALYSIS, "pressure_level", f"u_component_of_wind_500_{year}.nc")
    for year in era5_years
]
vwnd_files = [
    os.path.join(REANALYSIS, "pressure_level", f"v_component_of_wind_500_{year}.nc")
    for year in era5_years
]
eastward_flux_files = [
    os.path.join(
        REANALYSIS,
        "single_level",
        f"vertical_integral_of_eastward_water_vapour_flux_{year}.nc",
    )
    for year in era5_years
]
northward_flux_files = [
    os.path.join(
        REANALYSIS,
        "single_level",
        f"vertical_integral_of_northward_water_vapour_flux_{year}.nc",
    )
    for year in era5_years
]
temp_files = [
    os.path.join(REANALYSIS, "single_level", f"2m_temperature_{year}.nc")
    for year in era5_years
]

all_reanalysis_files = (
    [elevation_fname]
    + uwnd_files
    + vwnd_files
    + temp_files
    + eastward_flux_files
    + northward_flux_files
)


rule reanalysis:
    input:
        all_reanalysis_files,


################################################################################
# DEFAULT RULE
################################################################################


# default rule runs everything
rule all:
    input:
        all_nexrad_nc_files,
        all_reanalysis_files,
