"""
Keep track of how the Iowa State archive names files
"""

from datetime import datetime

from .const import *


def get_varname(dt: datetime):
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


def get_gz_fname(dt: datetime):
    """
    Get the filename of the `.grib2.gz` file.
    """
    varname = get_varname(dt)
    dt_str = dt.strftime(DT_FORMAT)
    fname = f"{varname}_00.00_{dt_str}.grib2.gz"
    return fname


def get_grib2_fname(dt: datetime):
    """
    Get the local .grib2 filename for a given date time
    """
    return get_gz_fname(dt).replace(".grib2.gz", ".grib2")


def get_nc_fname(dt: datetime):
    """
    Get the local .netcdf4 filename for a given date time
    """
    return get_gz_fname(dt).replace(".grib2.gz", ".nc")


def get_url(dt: datetime):
    """
    Get the URl of the file for a particular date-time snapshot
    """
    date_str = dt.strftime("%Y/%m/%d")
    fname = get_gz_fname(dt)
    varname = get_varname(dt)
    return f"https://mtarchive.geol.iastate.edu/{date_str}/mrms/ncep/{varname}/{fname}"
