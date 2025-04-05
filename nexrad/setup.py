from setuptools import setup, find_packages

setup(
    name="nexrad_utils",
    version="1.0",
    packages=find_packages(),
    long_description="Utilities for working with NEXRAD data",
    install_requires=[
        "datetime",
        "pandas",
        "tqdm",
    ],
)