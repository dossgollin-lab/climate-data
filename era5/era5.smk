ERA5_DATA_DIR = os.path.join(DATADIR, "ERA5")  # where the data goes
ERA5_SRC_DIR = os.path.join(HOMEDIR, "era5")  # this folder


configfile: os.path.join(ERA5_SRC_DIR, "era5_config.yml")


# turn command line arguments into strings
str_resolution = " --resolution {}".format(config["era5"]["resolution"])
str_bounds = " --lonmin {} --lonmax {} --latmin {} --latmax {}".format(
    config["era5"]["lonmin"],
    config["era5"]["lonmax"],
    config["era5"]["latmin"],
    config["era5"]["latmax"],
)
era5_env = os.path.join(ERA5_SRC_DIR, "era5_env.yml")


# get the elevation data file
elevation_fname = os.path.join(ERA5_DATA_DIR, "single_level", "elevation.nc")


rule era5_elevation:
    input:
        os.path.join(ERA5_SRC_DIR, "download_era5_orography.py"),
    output:
        elevation_fname,
    log:
        os.path.join(LOGS, "era5_elevation.log"),
    conda:
        era5_env
    shell:
        "python {input} --outfile {output}" + str_resolution + str_bounds


# get any variable on pressure levels
rule era5_pressure:
    input:
        os.path.join(ERA5_SRC_DIR, "download_era5_pressure.py"),
    output:
        os.path.join(ERA5_DATA_DIR, "pressure_level", "{variable}_{pressure}_{year}.nc"),
    log:
        os.path.join(LOGS, "era5_pressure", "{variable}_{pressure}_{year}.log"),
    conda:
        era5_env
    shell:
        (
            "python {input} --outfile {output} --variable {wildcards.variable} --pressure {wildcards.pressure} --year {wildcards.year}"
            + str_resolution
            + str_bounds
        )


# get any variable on a single level
rule era5_single_level:
    input:
        os.path.join(ERA5_SRC_DIR, "download_era5_single_level.py"),
    output:
        os.path.join(ERA5_DATA_DIR, "single_level", "{variable}_{year}.nc"),
    log:
        os.path.join(LOGS, "era5_single_level", "{variable}_{year}.log"),
    conda:
        era5_env
    shell:
        (
            "python {input} --outfile {output} --variable {wildcards.variable} --year {wildcards.year}"
            + str_resolution
            + str_bounds
        )


#  get all the ERA5 data
era5_years = range(config["era5"]["first_year"], config["era5"]["last_year"] + 1)

# specify the files to download
pressure_files = []
for year in era5_years:
    for var in config["era5"]["vars"]["pressure_level"]:
        varname = var["name"]
        levels = var["levels"]
        for level in levels:
            pressure_files.append(os.path.join(ERA5_DATA_DIR, "pressure_level", f"{varname}_{level}_{year}.nc"))

single_level_vars = config["era5"]["vars"]["single_level"]
single_level_files = [
    os.path.join(ERA5_DATA_DIR, "single_level", f"{var}_{year}.nc")
    for year in era5_years
    for var in single_level_vars
]


# explicitly list the files to download
all_reanalysis_files = [elevation_fname] + pressure_files + single_level_files


# the rule to download all the ERA5 data
rule ERA5:
    input:
        all_reanalysis_files,
