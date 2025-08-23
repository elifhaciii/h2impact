## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/elifhaciii/h2impact.git
cd h2impact

```

### 2. Requirements

```bash
pip install -r requirements.txt

python setup_pypsa_env.py

``` 

###  3. Downloading Data
Sign up to CDS website. Then,to use your API key, create a file called `~/.cdsapirc` in your home directory. Configure the file:

```ini
url: https://cds.climate.copernicus.eu/api/v2
key: <UID>:<API-KEY>

```






1. Prerequisites
Python 3.8+ installed

cdsapi Python package:

sh
Copy
Edit
pip install cdsapi xarray netcdf4
CDS API key saved as ~/.cdsapirc (see official guide)

2. Download Monthly ERA5 Data
Script: src/h2impact/data/download_monthlydata.py

Usage Example:

sh
Copy
Edit
python src/h2impact/data/download_monthlydata.py \
  -s 2013-05-01 \
  -e 2013-05-31 \
  -o tmp_monthly_nc/era5_2013-05.nc \
  --area 56.0 4.0 46.0 15.0
Arguments:

-s / --start-date — Start date (YYYY-MM-DD), e.g. 2013-05-01

-e / --end-date — End date (YYYY-MM-DD), e.g. 2013-05-31

-o / --output — Output file path, e.g. tmp_monthly_nc/era5_2013-05.nc

--area — Geographic bounding box as N W S E (default: 56.0 4.0 46.0 15.0)

Tip:
Repeat for each month/year you want.
Example for a full year (Jan–Dec):

sh
Copy
Edit
for m in {1..12}; do
  python src/h2impact/data/download_monthlydata.py \
    -s 2013-$(printf "%02d" $m)-01 \
    -e 2013-$(printf "%02d" $m)-28 \
    -o tmp_monthly_nc/era5_2013-$(printf "%02d" $m).nc \
    --area 56.0 4.0 46.0 15.0
done
(Adjust the end date for each month as needed.)

3. Merge Monthly NetCDF Files
Script: src/h2impact/data/merge_nc_files_friendly.py

Basic Usage:

sh
Copy
Edit
python src/h2impact/data/merge_nc_files_friendly.py \
  -i tmp_monthly_nc \
  -o src/h2impact/data/cutouts/it-2013-05.nc
-i — Input folder with your monthly .nc files

-o — Output merged .nc file

To merge only specific months:

sh
Copy
Edit
python src/h2impact/data/merge_nc_files_friendly.py \
  -i tmp_monthly_nc \
  -o src/h2impact/data/cutouts/it-2013-q1.nc \
  --months 1 2 3
To merge selected files:

sh
Copy
Edit
python src/h2impact/data/merge_nc_files_friendly.py \
  -i tmp_monthly_nc \
  -o src/h2impact/data/cutouts/it-2013-01-02.nc \
  --files era5_2013-01.nc era5_2013-02.nc
4. Output Locations
Downloaded files: tmp_monthly_nc/ (create this folder if it does not exist)

Final merged cutout: src/h2impact/data/cutouts/ (create if needed)

Tip:
Use .gitignore to avoid pushing large data files.

5. Troubleshooting
cdsapi issues: Check your ~/.cdsapirc file and API credentials.

File merge errors: Make sure all monthly .nc files exist and are not corrupted.

Out of disk space: ERA5 data can be large; check available disk space before downloading a year.

6. Example: Download and Merge a Year for Italy
sh
Copy
Edit
# Step 1: Download all months
for m in {1..12}; do
  python src/h2impact/data/download_monthlydata.py \
    -s 2013-$(printf "%02d" $m)-01 \
    -e 2013-$(printf "%02d" $m)-28 \
    -o tmp_monthly_nc/era5_2013-$(printf "%02d" $m).nc \
    --area 47.1 6.6 36.5 18.5
done

# Step 2: Merge into a single file
python src/h2impact/data/merge_nc_files_friendly.py \
  -i tmp_monthly_nc \
  -o src/h2impact/data/cutouts/it-2013.nc


### Quick Test: Download a Single Day

To check that your setup works, try downloading a single day's data (this is fast and small):

```sh
python src/h2impact/data/download_monthlydata.py \
  -s 2013-05-01 \
  -e 2013-05-01 \
  -o tmp_monthly_nc/era5_test.nc \
  --area 56.0 4.0 56.0 4.0
If the script runs and saves era5_test.nc (even if it’s tiny), your CDS credentials and environment are correct!
If you see an authentication or connection error, check your .cdsapirc file and your internet connection.


Generate a Scenario Config File (No H₂)
This script helps you quickly generate a configuration YAML for PyPSA-Eur without hydrogen (“no H₂” scenario).

What does "no H₂" mean?
In this context, “no H₂” (no hydrogen) means the scenario:

Does not include hydrogen production, storage, or use.

No hydrogen electrolyzers or hydrogen storage units are enabled.

No hydrogen pipelines or related infrastructure are modeled.

All energy demand is met without hydrogen as a fuel or carrier.

This allows you to compare energy systems with and without hydrogen to assess the impact of hydrogen on costs, renewables, and emissions.

📝 How to Generate the Config File
Script location:

bash
Copy
Edit
src/h2impact/generate_config_noH2.py
Run the script:

bash
Copy
Edit
python src/h2impact/generate_config_noH2.py
You’ll be prompted for:

Cutout name (e.g. de-2013-05)

Path to NetCDF weather file

Longitude min & max (e.g., 6.6, 18.5)

Latitude min & max (e.g., 36.5, 47.1)

Start date and end date (YYYY-MM-DD)

Country code(s) (e.g. IT or DE,FR)

Example:

pgsql
Copy
Edit
---- PyPSA-Eur Scenario Config Generator ----
Enter cutout name (e.g., de-2013-05): it-2013-05
Enter path to cutout NetCDF file: ../../src/h2impact/data/cutouts/it-2013-05.nc
Longitude min (e.g., 6.6): 6.6
Longitude max (e.g., 18.5): 18.5
Latitude min (e.g., 36.5): 36.5
Latitude max (e.g., 47.1): 47.1
Start date (YYYY-MM-DD): 2013-05-01
End date (YYYY-MM-DD): 2013-05-31
Country code(s) (e.g., IT): IT
The script will generate a config file in:

bash
Copy
Edit
src/h2impact/configs/
🚦 How to Run the Scenario
After creating your config file, run the Snakemake workflow (from the external/pypsa-eur folder):

bash
Copy
Edit
cd external/pypsa-eur
snakemake -j1 --configfile ../../src/h2impact/configs/config_no_H2_it-2013-05.yaml
Output files (including .nc result files) will appear in the results or resources folder as configured.

ℹ️ Note:
This script is only for “no hydrogen” scenarios. For H₂-enabled analyses, use the relevant script or config.

⚡ Generate a Scenario Config File (H₂ Enabled)
This script helps you quickly generate a configuration YAML for PyPSA-Eur with hydrogen enabled (“H₂ scenario”).

What does "H₂ enabled" mean?
In this context, “H₂ enabled” means the scenario:

Includes hydrogen production via electrolyzers

Allows hydrogen storage and infrastructure (e.g. storage units, pipelines, links)

Hydrogen is available as a fuel and can participate in sector coupling, flexibility, and storage

Use this scenario to study the role and impact of hydrogen on the energy system.

📝 How to Generate the Config File
Script location:

bash
Copy
Edit
src/h2impact/generate_config_H2.py
Run the script:

bash
Copy
Edit
python src/h2impact/generate_config_H2.py
You’ll be prompted for:

Cutout name (e.g. de-2013-05)

Path to NetCDF weather file

Longitude min & max (e.g., 6.6, 18.5)

Latitude min & max (e.g., 36.5, 47.1)

Start date and end date (YYYY-MM-DD)

Country code(s) (e.g. IT or DE,FR)

Example:

pgsql
Copy
Edit
---- PyPSA-Eur H₂ Scenario Config Generator ----
Enter cutout name (e.g., de-2013-05): it-2013-05
Enter path to cutout NetCDF file: ../../src/h2impact/data/cutouts/it-2013-05.nc
Longitude min (e.g., 6.6): 6.6
Longitude max (e.g., 18.5): 18.5
Latitude min (e.g., 36.5): 36.5
Latitude max (e.g., 47.1): 47.1
Start date (YYYY-MM-DD): 2013-05-01
End date (YYYY-MM-DD): 2013-05-31
Country code(s) (e.g., IT): IT
The script will generate a config file in:

bash
Copy
Edit
src/h2impact/configs/
🚦 How to Run the Scenario
After creating your config file, run the Snakemake workflow (from the external/pypsa-eur folder):

bash
Copy
Edit
cd external/pypsa-eur
snakemake -j1 --configfile ../../src/h2impact/configs/config_H2_it-2013-05.yaml
Output files (including .nc result files) will appear in the results or resources folder as configured.

ℹ️ Note:
This script is only for hydrogen-enabled scenarios. For scenarios without hydrogen, use the generate_config_noH2.py script.

### Running PyPSA-Eur and Collecting Results
After you have created your configuration YAML files (using the provided Python scripts), you can run the PyPSA-Eur Snakemake pipeline and automatically save the result .nc files with clear scenario names.

1. Running the No-Hydrogen (NoH2) Scenario
Use the run_pypsaeur_H2disenabled.sh script to execute the workflow and copy the result file.
Usage:

bash
Copy
Edit
bash run_pypsaeur_H2disenabled.sh <path-to-config-noH2-yaml>
Example:

bash
Copy
Edit
bash run_pypsaeur_H2disenabled.sh src/h2impact/configs/config_no_H2_it-2013-05.yaml
This will:

Run the PyPSA-Eur workflow with your configuration.

Copy the resulting .nc file to results/it-2013-05-nohydrogen-result.nc (filename will be customized based on your config).

2. Running the Hydrogen-Enabled (H2) Scenario
Use the run_pypsaeur_H2enabled.sh script to execute the workflow for a scenario with hydrogen enabled.
Usage:

bash
Copy
Edit
bash run_pypsaeur_H2enabled.sh <path-to-config-H2-yaml>
Example:

bash
Copy
Edit
bash run_pypsaeur_H2enabled.sh src/h2impact/configs/config_H2_it-2013-05.yaml
This will:

Run the PyPSA-Eur workflow with your configuration.

Copy the resulting .nc file to results/it-2013-05-hydrogen-result.nc (filename will be customized based on your config).

Notes
Both scripts must be run from the project’s root directory.

The results/ folder will be created if it does not exist.

The output filenames will always include the country and time window (from your config), and will have either -nohydrogen-result.nc or -hydrogen-result.nc as a suffix for clarity.

These scripts make it easy to compare the outputs of your no-H2 and H2-enabled scenarios.

📊 Postprocessing & Scenario Comparison
This section explains how to compare results from the H2-enabled and H2-disenabled scenarios, using the compare_scenarios.py script.

1. What Does This Script Do?
Loads the result .nc (NetCDF) files produced by your two PyPSA-Eur runs (one with hydrogen, one without).

Compares important results (e.g., total system cost, CO₂ emissions, renewable generation, storage, etc.).

Outputs a summary table and (optionally) generates plots.

2. Where to Find or Put the Script
Place the script at:

bash
Copy
Edit
src/h2impact/postprocess/compare_scenarios.py
3. How to Use
Example command (from your project root):

bash
Copy
Edit
python src/h2impact/postprocess/compare_scenarios.py \
    results/be-2013-05-nohydrogen-result.nc \
    results/be-2013-05-result-H2.nc
Replace the filenames above with your own result files as appropriate.

4. Expected Output
The script prints a summary comparison to the console.

Optionally, it can generate comparison plots (see script options/help).

5. Requirements
Python 3.8+

Packages: xarray, matplotlib, numpy, pandas, etc.

Run pip install -r requirements.txt if needed.

Note: Make sure to run your PyPSA-Eur scenarios first, and that both result files are present in your results/ directory.





