from datetime import datetime
from tqdm import tqdm

import pandas as pd

from .const import MISSING_SNAPSHOTS
from .namingconventions import *


class BoundingBox:
    def __init__(
        self,
        lonmin: float = 230,
        lonmax: float = 300,
        latmin: float = 20,
        latmax: float = 55,
    ) -> None:
        """
        Bounding box for the data to retain.
        The valid boundaries are lon in [230, 300] and lat in [20, 55]
        """

        self.latmin = latmin
        self.latmax = latmax
        self.lonmin = lonmin
        self.lonmax = lonmax

        self.assert_valid_longitudes()
        self.assert_valid_latitudes()

    def assert_valid_longitudes(self) -> None:
        """Make sure the longitudes are valid"""
        assert (
            self.lonmin < self.lonmax
        ), "min longitude must be less than max longitude"
        assert self.lonmin >= 230, "min longitude must be at least 230"
        assert self.lonmax <= 300, "max longitude must be no greater than 300"

    def assert_valid_latitudes(self) -> None:
        """Make sure the latitudes are valid"""
        assert self.latmin < self.latmax, "min latitude must be less than max latitude"
        assert self.latmin >= 20, "min latitude must be at least 20"
        assert self.latmax <= 55, "max latitude must be at least 55"


def assert_valid_datetime(dt: datetime) -> None:
    """
    Do any needed checks on the data
    """
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    assert dt >= GAUGECORR_BEGINTIME, f"Data is not available for {dt_str}"
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0


class TimeRange:
    """Shallow rapper for pandas.date_range with some checks"""

    def __init__(self, stime: datetime, etime: datetime) -> None:

        assert_valid_datetime(stime)
        assert_valid_datetime(etime)
        self.stime = stime
        self.etime = etime
        self.dts = pd.date_range(self.stime, self.etime, freq="H")

    def printbounds(self) -> str:
        fmt = "%Y-%m-%d %H:%M:%S"
        return self.stime.strftime(fmt) + " to " + self.etime.strftime(fmt)
