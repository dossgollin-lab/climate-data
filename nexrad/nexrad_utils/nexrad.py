from datetime import datetime
from tqdm import tqdm

import pandas as pd

from .const import MISSING_SNAPSHOTS
from .namingconventions import *


def assert_valid_datetime(dt: datetime) -> None:
    """
    Do any needed checks on the data
    """
    dt_str = dt.strftime("%Y%m%d-%H%M%S")
    assert dt >= GAUGECORR_BEGINTIME, f"Data is not available for {dt_str}"
    assert dt.minute == 0
    assert dt.second == 0
    assert dt.microsecond == 0
    assert dt not in MISSING_SNAPSHOTS, f"Data is missing for {dt_str}"


class TimeRange:
    """Shallow rapper for pandas.date_range with some checks"""

    def __init__(self, stime: datetime, etime: datetime) -> None:
        assert_valid_datetime(stime)
        assert_valid_datetime(etime)
        self.stime = stime
        self.etime = etime
        self.dt_all = pd.date_range(self.stime, self.etime, freq="h")
        self.dt_valid = [dt for dt in self.dt_all if dt not in MISSING_SNAPSHOTS]

    def printbounds(self) -> str:
        fmt = "%Y-%m-%d %H:%M:%S"
        return self.stime.strftime(fmt) + " to " + self.etime.strftime(fmt)
