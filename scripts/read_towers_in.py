## Read towers in
import zipfile
from pathlib import Path
import pandas as pd

keep = ["TIMESTAMP_START", "TIMESTAMP_END", "TA_F", "SW_IN_F", "VPD_F", "P_F",
        "NETRAD", "G_F_MDS", "H_F_MDS", "H_F_MDS_QC", "LE_F_MDS", "LE_F_MDS_QC",
        "NEE_VUT_REF", "NEE_VUT_REF_QC", "GPP_NT_VUT_REF", "RECO_NT_VUT_REF"]

zip_file = sorted(Path("data/raw").glob("*.zip"))[0]
with zipfile.ZipFile(zip_file) as z:
    hh_name = [n for n in z.namelist() if "FLUXMET_HH" in n][0]
    with z.open(hh_name) as f:
        hh = pd.read_csv(f, na_values=[-9999],
                         usecols=lambda c: c in keep,
                         dtype={"TIMESTAMP_START": str, "TIMESTAMP_END": str})

hh["time"] = pd.to_datetime(hh["TIMESTAMP_START"], format="%Y%m%d%H%M")
print(len(hh), hh["time"].min(), hh["time"].max())
print((hh["NEE_VUT_REF_QC"] == 0).mean())    # share of measured NEE

print(hh["time"].describe())

# count rows per year
hh["year"] = hh["time"].dt.year
print(hh.groupby("year").size())

#check if there are no duplicated time stamps
print(hh["time"].duplicated().sum())

print(hh["TA_F"].describe())

#Wrap it in a function
# Turn B2 into a function read_hh(zip_file) that returns one tidy table with a site 
# column (the site ID from the file name), then read all five towers into one table. 
# You will reuse this function in Block 5.
def read_hh(zip_file):
    site = zip_file.stem.split("_")[1]
    with zipfile.ZipFile(zip_file) as z:
        hh_name = [n for n in z.namelist() if "FLUXMET_HH" in n][0]
        with z.open(hh_name) as f:
            hh = pd.read_csv(f, na_values=[-9999],
                             usecols=lambda c: c in keep,
                             dtype={"TIMESTAMP_START": str, "TIMESTAMP_END": str})
    hh["time"] = pd.to_datetime(hh["TIMESTAMP_START"], format="%Y%m%d%H%M")
    hh["site"] = site
    return hh

zip_files = sorted(Path("data/raw").glob("*.zip"))
towers = pd.concat([read_hh(z) for z in zip_files], ignore_index=True)
print(towers["site"].unique())
towers.describe()

# tower tabelle speichern
towers.to_csv("data/processed/towers.csv", index=False)
