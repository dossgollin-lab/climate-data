import datetime
from typing import List

# there are some snapshots that are known to be missing data
MISSING_SNAPSHOTS: List[datetime.datetime] = []  # TODO: all the missing data goes here

# when does the GaugeCorr_QPE_01H data start
STIME = datetime.datetime(2000, 1, 1, 0)  # TODO: is this really the first day?

# when the MultiSensor_QPE_01H_Pass2 data becomes available TODO: update, this isn't exact yet
MULTISENSOR_CUTOFF = datetime.date(2020, 10, 1)
