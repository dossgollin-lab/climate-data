"""
Keep track of how the Iowa State archive names files
"""

from datetime import datetime
import os

from .const import *


def get_varname(dt: datetime) -> str:
    """
    Get the variable name for a particular date-time snapshot
    """
    if dt >= MULTISENSOR_BEGINTIME:
        var = "MultiSensor_QPE_01H_Pass2"
    elif GAUGECORR_BEGINTIME <= dt < MULTISENSOR_BEGINTIME:
        var = "GaugeCorr_QPE_01H"
    else:
        dt_str = dt.strftime(DT_FORMAT)
        raise ValueError(f"No data for {dt_str}")
    return var


def get_fname_base(dt: datetime, dirname: str = None) -> str:
    """
    Get the base filename for a particular date-time snapshot (no extension)
    """
    varname = get_varname(dt)
    dt_str = dt.strftime(DT_FORMAT)
    dt_year = dt.strftime("%Y")
    dt_month = dt.strftime("%m")
    dt_day = dt.strftime("%d")
    dt_fname = f"{varname}_00.00_{dt_str}"

    # Generate the nested path
    fname = os.path.join(dt_year, dt_month, dt_day, dt_fname)
    if dirname:
        fname = os.path.join(dirname, fname)

    return fname


def get_gz_fname(dt: datetime, dirname: str = None) -> str:
    """
    Get the filename of the `.grib2.gz` file.
    """
    return get_fname_base(dt=dt, dirname=dirname) + ".grib2.gz"


def get_grib2_fname(dt: datetime, dirname: str = None) -> str:
    """
    Get the local .grib2 filename for a given date time
    """
    return get_fname_base(dt=dt, dirname=dirname) + ".grib2"


def get_nc_fname(dt: datetime, dirname: str = None) -> str:
    """
    Get the local .netcdf4 filename for a given date time
    """
    return get_fname_base(dt=dt, dirname=dirname) + ".nc"


def get_url(dt: datetime) -> str:
    """
    Get the URl of the file for a particular date-time snapshot
    """
    date_str = dt.strftime("%Y/%m/%d")
    fname = get_gz_fname(dt)

    # drop the folder structure
    fname = fname.split("/")[-1]

    varname = get_varname(dt)
    return f"https://mtarchive.geol.iastate.edu/{date_str}/mrms/ncep/{varname}/{fname}"


def fname2dt(fname: str) -> datetime:
    """
    Parse a filename to get the corresponding datetime
    """
    # Extract the filename part, ignoring the directory structure
    basename = os.path.basename(fname)

    # Extract the datetime string from the basename
    dt_str = basename.split("_00.00_")[1].split(".")[0]

    # Parse the datetime string to a datetime object
    return datetime.strptime(dt_str, DT_FORMAT)


def fname2url(fname: str) -> str:
    """
    Given the filename, get the corresponding
    """
    dt = fname2dt(fname)
    return get_url(dt)
