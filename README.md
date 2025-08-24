# H2Impact

A reproducible extension of PyPSA-Eur to assess the impact of hydrogen integration into the European electricity system.

### 1. Clone the Repository

```bash
git clone https://github.com/elifhaciii/h2impact.git
cd h2impact

```

### 2. Requirements

Some features of h2impact depend on PyPSA-Eur
,a full-featured energy system modeling framework. You need to install it separately. You can follow the instructions in PyPSA-Eur website: https://pypsa-eur.readthedocs.io/en/latest/installation.html 

PyPSA passes the PyPSA-Eur network model to an external solver for performing the optimisation. 

Install HIGHS solver: 

```bash
conda install -c conda-forge highs

```
For other required packages install:

```bash
pip install -r requirements.txt

``` 

###  3. Downloading Data

This project includes a script to download ERA5 reanalysis cutouts from the Copernicus Climate Data Store (CDS)

First, make sure that you have a CDS account, you can sign up free. Then create a ~/.cdsapirc file and to easily use your API token, you can configure it inside your .cdsapirc file:

```ini
url: https://cds.climate.copernicus.eu/api/v2
key: <UID>:<API-KEY>

```

Always run from the project root:

```ini
python -m src.h2impact.data.download_era5_cutout --year <input> --region <country name> --month <month_number>

```

An example:

```ini

# Download January 2020 for Germany
python -m src.h2impact.data.download_era5_cutout --year 2020 --region germany --month 1

```

The zipped .nc file is saved under cutouts folder.

To unzip the file and merge _accum.nc and _instant.nc files, use the script: 

```ini

bash scripts/process_and_merge_era5_cutouts.sh <country_code> 2020

```

###  4. Generating configuration files

This step sets up .yaml configuration files based on downloaded ERA5 cutouts and selected countries. There are two main scenarios in this project: H2 related technologies enabled and disabled.

#### H2 disabled scenario

From the root of the project, run:

```ini

python -m src.h2impact.configs.generate_config_noH2

```
#### H2 enabled scenario

```ini

python -m src.h2impact.configs.generate_config_H2

```

The generated YAML files are saved under:

```ini

src/h2impact/configs/yaml_files/config_no_H2_<cutout_name>.yaml
src/h2impact/configs/yaml_files/config_H2_<cutout_name>.yaml

```

Tip: You don't need to enter bounding box coordinates or time range — they are automatically detected using internal mappings and NetCDF metadata.


Test case: 

```ini

src/h2impact/configs/yaml_files/config_no_H2_DE_2020_01_merged.yaml
src/h2impact/configs/yaml_files/config_H2_DE_2020_01_merged.yaml

```

###  5. Execution of Snakemake workflow

Navigate into the external/pypsa-eur directory:


```ini
cd external/pypsa-eur

```

Run actual Snakemake workflow using the configuration file:

```ini
snakemake -j8 --configfile ../../src/h2impact/configs/yaml_files/<CONFIG_FILENAME>.yaml

```

Optionally, you can preview which rules will be running using:

```ini
snakemake -j8 --configfile ../../src/h2impact/configs/yaml_files/<CONFIG_FILENAME>.yaml --dry-run

```
Test case:
```ini
snakemake -j1 --configfile src/h2impact/configs/yaml_files/config_H2_DE_2020_01_merged.yaml
```

###  6. Postprocessing

There are 10 different scripts for possible postproccesing of the output file of Snakemake workflow. All scripts run in the same logic.

Use command:

```ini
python src/h2impact/postprocess/<script_name>.py --input <path_to_result.nc>

```

### Possible Issues

Due to environment/compatibility challenges, full Snakemake execution may fail. However, YAML templates are auto-generated, and input data is prepared according to PyPSA-Eur structure. Postprocessing scripts operate on expected outputs.

You can access test ERA5 .nc cutout files, configuration .yaml files, result .nc files and post processing examples in the tests folder.

