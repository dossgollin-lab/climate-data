"""
This script download the GHCN files for daily precipitation of all stations and transfer them to nc files
units for output prcp: mm/day

The original GHCN data from https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/
GHCN-D readme file https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/doc/GHCND_documentation.pdf
"""

import pandas as pd
import numpy as np
import xarray as xr

import requests # Downloading file via requests
import tarfile # extract tar raw file

from tqdm import tqdm # showing progress


"""
Codes for reading stations txt metadata
"""

# Metadata specs

METADATA_COL_SPECS = [
    (0, 12),
    (12, 21),
    (21, 31),
    (31, 38),
    (38, 41),
    (41, 72),
    (72, 76),
    (76, 80),
    (80, 86),
]

METADATA_NAMES = [
    "ID",
    "LATITUDE",
    "LONGITUDE",
    "ELEVATION",
    "STATE",
    "NAME",
    "GSN FLAG",
    "HCN/CRN FLAG",
    "WMO ID",
]

METADATA_DTYPE = {
    "ID": str,
    "STATE": str,
    "NAME": str,
    "GSN FLAG": str,
    "HCN/CRN FLAG": str,
    "WMO ID": str,
}

def read_station_metadata(filename="ghcnd-stations.txt"):
    """Reads in station metadata
    :filename: ghcnd station metadata file.
    :returns: station metadata as a pandas Dataframe
    """
    return pd.read_fwf(
        filename,
        METADATA_COL_SPECS,
        names=METADATA_NAMES,
        index_col="ID",
        dtype=METADATA_DTYPE,
    )


"""
Codes for reading GHCN csv file extracted from the tar.gz file
"""

def get_ghcn_data(lon, lat, stnid: str):
    """Reads in all data from a GHCN .csv data file
    read in as Pandas dataframe, transfer to dataset
    """
    fname = f"/Volumes/research/jd82/GHCN/tmp/{stnid}.csv"
    df = pd.read_csv(fname)[["DATE", "PRCP"]]
    df[["PRCP"]] = df[["PRCP"]] / 10 # original unit tenths of mm, to mm/day

    df["DATE"] = pd.to_datetime(df["DATE"])
    time = df.iloc[:, 0].values
    prcp = np.reshape(df.iloc[:, 1].values, (-1, 1))

    ds = xr.Dataset(
        {"prcp": xr.DataArray(
            data = prcp,
            dims = ["time", "ID"],
            coords = {"time": time, "ID": [stnid]},
            attrs = {"units": "mm/d"}
        ),
         "lat": xr.DataArray(
            data = np.array([lat]),
            dims = ["ID"],
            coords = {"ID": [stnid]},
        ),
         "lon": xr.DataArray(
            data = np.array([lon]),
            dims = ["ID"],
            coords = {"ID": [stnid]},
        ),   
        },
    )

    return df, ds


def main() -> None:
    """Run everything"""
    

    """
    # download and extract the raw files
    # since the file is large, slow to download and extract, the raw csvs are already within the folder
    
    # if the raw tar file is available
    # extract them to individual csv files
    try:
        GHCN_raw = tarfile.open("/Volumes/research/jd82/GHCN/GHCN_raw.tar.gz", "r:gz")
        GHCN_raw.extractall(path = "/Volumes/research/jd82/GHCN/tmp")
        GHCN_raw.close()
    # or download the tar file and extract
    except:
        url_prcp = "https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/archive/daily-summaries-latest.tar.gz"
        response_prcp = requests.get(url_prcp, stream=True)
        with open("GHCN_raw.tar.gz", "wb") as f:
            f.write(response_prcp.content)
        
        GHCN_raw = tarfile.open("/Volumes/research/jd82/GHCN/GHCN_raw.tar.gz", "r:gz")
        GHCN_raw.extractall(path = "/Volumes/research/jd82/GHCN/tmp")
        GHCN_raw.close()
    """
    

    # Get metadata for all stations
    url_meta = "https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/doc/ghcnd-stations.txt"
    response_meta = requests.get(url_meta, stream=True)
    with open("/Volumes/research/jd82/GHCN/ghcnd-stations.txt", "wb") as f:
        f.write(response_meta.content)
    # all stations, without any filters
    stations = (
        read_station_metadata("/Volumes/research/jd82/GHCN/ghcnd-stations.txt")
        .reset_index()[["ID", "LATITUDE", "LONGITUDE", "STATE", "NAME"]]
    )
    # add a column for number of observations
    stations["n_obs"] = ''
    
    valid_ids = [stnid for stnid in stations["ID"]]


    # transfer csv file to nc files for all stations
    for i in tqdm(range(len(valid_ids))):
        stnid = valid_ids[i]
        try:
            # metadata for this specific station
            stnid_tmp = stations.loc[stations['ID'] == stnid]
            lat_tmp = stnid_tmp.iloc[0, 1]
            lon_tmp = stnid_tmp.iloc[0, 2]
            df_tmp, ds_tmp = get_ghcn_data(lon_tmp, lat_tmp, stnid)
            ds_tmp.to_netcdf(f"/Volumes/research/jd82/GHCN/daily_prcp/{stnid}.nc")

            stations[i, 5] = df_tmp.dropna().shape[0]
        except:
            None
            # print("{stnid} not found"

    stations.to_csv("/Volumes/research/jd82/GHCN/stations_metadata.csv")
    
if __name__ == "__main__":
    main()