from distutils.core import setup

setup(
    name="util",
    version="1.0",
    packages=[
        "util",
    ],
    long_description="helpful tools for this analysis",
    install_requires=[
        "datetime",
        "pandas",
        "tqdm",
    ],
)
