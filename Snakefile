from datetime import datetime
import platform
import os

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
LOGS = os.path.join(HOMEDIR, "logs")


# include each of the sub-snakefiles
include: "nexrad/nexrad.smk"
include: "era5/era5.smk"


# default rule runs everything
rule all:
    input:
        all_nexrad_nc_files,
        all_reanalysis_files,
