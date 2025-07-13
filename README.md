h2impact: Weather Data Download and Merge Guide
Downloading ERA5 Weather Data
This project uses ERA5 weather data as input for energy system modelling.
Follow these steps to download and merge monthly weather data as NetCDF files.

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
