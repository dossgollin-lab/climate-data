import datetime
from multiprocessing.sharedctypes import Value
from urllib.request import urlretrieve

import xarray as xr

from .path import datadir


def is_valid(dt: datetime.date):
    """Make sure the date is valid"""
    sdate = datetime.datetime(2000, 1, 1, 0)  # TODO: is this really the first day?
    if dt < sdate:
        dt_str = dt.strftime("%Y%m%d-%H%M%S")
        raise ValueError(f"Data is not available for {dt_str}")


def get_varname(dt: datetime.date):
    """
    Get the variable name for a particular date-time snapshot

    Refer to email from Jian Zhang, July 7 2022
    """
    cutoff = datetime.date(2020, 10, 1)  # TODO: update, this isn't exact yet
    if dt > cutoff:
        var = "MultiSensor_QPE_01H_Pass2"
    else:
        var = "GaugeCorr_QPE_01H"

    return f"{var}_00.00"  # TODO: make sure the GaugeCorr data looks like this


def gz_fname(dt: datetime.date, local=False):
    """
    Get the filename of the `.grib2.gz` file. If `local=True` then returns the
    full local path.
    """
    varname = get_varname(dt)
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    fname = f"{varname}_{dt_str}.grib2.gz"
    if local:
        fname = datadir(fname)
    return fname


def grib2_fname(dt: datetime.date):
    """
    Get the local .grib2 filename for a given date time
    """
    return gz_fname(dt).replace(".grib2.gz", ".grib2")


def get_url(dt: datetime.date):
    """
    Get the URl of the file for a particular date-time snapshot
    """
    date_str = dt.strftime("%Y/%m/%d")
    fname = gz_fname(dt)
    return (
        f"https://mtarchive.geol.iastate.edu/"
        f"{date_str}/mrms/ncep/MultiSensor_QPE_01H_Pass2/"
        f"{fname}"
    )
