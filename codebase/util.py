"""
Shallow wrappers around standard python functions to simplify syntax
"""

from urllib.request import urlretrieve
import os
import gzip
import shutil


def unzip_gz(fname_in: str, fname_out: str) -> None:
    """Unzip a GZ file"""
    with gzip.open(fname_in, "rb") as f_in:
        with open(fname_out, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def download_file(url: str, fname: str) -> None:
    """Download a file from a URL"""
    urlretrieve(url, fname)


def delete_file(fname: str) -> None:
    """Delete a file"""
    os.remove(fname)


def ensure_dir(dirname: str) -> None:
    """Make sure a directory exists"""
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
