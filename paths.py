import datetime


def get_url(dt: datetime.date):
    date_str = dt.strftime("%Y/%m/%d")
    date_str2 = dt.strftime("%Y%m%d-%H%M%S")
    return (
        f"https://mtarchive.geol.iastate.edu/"
        f"{date_str}/mrms/ncep/MultiSensor_QPE_01H_Pass2/"
        "MultiSensor_QPE_01H_Pass2_00.00_{date_str2}.grib2.gz"
    )
