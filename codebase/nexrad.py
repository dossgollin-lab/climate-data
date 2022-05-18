import datetime
from urllib.request import urlretrieve

import xarray as xr

from .path import datadir



def gz_fname(dt: datetime.date, local=False):
    """
    Get the filename of the `.grib2.gz` file. If `local=True` then returns the
    full local path.
    """
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    fname = f"MultiSensor_QPE_01H_Pass2_00.00_{dt_str}.grib2.gz"
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

