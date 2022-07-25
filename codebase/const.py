from datetime import datetime
from typing import List

# there are some snapshots that are known to be missing data
MISSING_SNAPSHOTS: List[datetime] = []  # TODO: all the missing data goes here

# when does the GaugeCorr_QPE_01H data start
GAUGECORR_BEGINTIME = datetime(2015, 5, 6, 20)

# when the MultiSensor_QPE_01H_Pass2 data becomes available
MULTISENSOR_BEGINTIME = datetime(2020, 10, 13, 19)

# the datetime format used by the Iowa State archive
DT_FORMAT = "%Y%m%d-%H%M%S"
