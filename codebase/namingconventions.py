"""
Keep track of how the Iowa State archive names files
"""

import datetime

from .const import *

def get_varname(dt: datetime.date):
    """
    Get the variable name for a particular date-time snapshot
    """
    if dt > MULTISENSOR_CUTOFF:
        var = "MultiSensor_QPE_01H_Pass2"
    else:
        var = "GaugeCorr_QPE_01H"

    return var


def get_gz_fname(dt: datetime.date, local=False):
    """
    Get the filename of the `.grib2.gz` file.
    If `local=True` then returns the full local path.
    """
    varname = get_varname(dt)
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    fname = (
        f"{varname}_00.00_{dt_str}.grib2.gz"  # TODO: make sure this is the right format
    )
    return fname


def get_grib2_fname(dt: datetime.date):
    """
    Get the local .grib2 filename for a given date time
    """
    return get_gz_fname(dt).replace(".grib2.gz", ".grib2")


def get_nc_fname(dt: datetime.date):
    """
    Get the local .netcdf4 filename for a given date time
    """
    return get_gz_fname(dt).replace(".grib2.gz", ".nc")


def get_url(dt: datetime.date):
    """
    Get the URl of the file for a particular date-time snapshot
    """
    date_str = dt.strftime("%Y/%m/%d")
    fname = get_gz_fname(dt)
    return (
        f"https://mtarchive.geol.iastate.edu/"
        f"{date_str}/mrms/ncep/MultiSensor_QPE_01H_Pass2/"
        f"{fname}"
    )
