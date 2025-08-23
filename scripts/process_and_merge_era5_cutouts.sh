#!/bin/bash

# === Args ===
CODE=$1
YEAR=$2
DIR=${3:-cutouts}

if [ -z "$CODE" ] || [ -z "$YEAR" ]; then
  echo "Usage: bash process_and_merge_era5_cutouts.sh <COUNTRY_CODE> <YEAR> [DATA_DIR]"
  exit 1
fi

echo "Working in: $DIR"
echo "Country: $CODE"
echo "Year: $YEAR"
echo ""

# === Unzip and rename ===
for zip_file in ${DIR}/${CODE}_${YEAR}_*.nc; do
  [ -e "$zip_file" ] || continue

  filename=$(basename -- "$zip_file")
  month=$(echo "$filename" | grep -oE '_[0-9]{4}_[0-9]{2}' | cut -d_ -f3)

  echo "Processing zip: $filename (Month: $month)"

  tmp_dir="${DIR}/tmp_$month"
  mkdir -p "$tmp_dir"

  unzip -o "$zip_file" -d "$tmp_dir"

  mv "$tmp_dir"/data_stream-oper_stepType-instant.nc "${DIR}/${CODE}_${YEAR}_${month}_instant.nc"
  mv "$tmp_dir"/data_stream-oper_stepType-accum.nc   "${DIR}/${CODE}_${YEAR}_${month}_accum.nc"

  rm -r "$tmp_dir"

  echo "Extracted: ${CODE}_${YEAR}_${month}_instant.nc + _accum.nc"
  echo ""
done

# === Merge each month ===
echo "Merging monthly files..."
PYTHON_CODE=$(cat <<EOF
import xarray as xr
from pathlib import Path
import sys

code = "${CODE}"
year = "${YEAR}"
cutout_dir = Path("${DIR}")

rename_map = {
    "10m_u_component_of_wind": "u10",
    "10m_v_component_of_wind": "v10",
    "2m_temperature": "t2m",
    "surface_solar_radiation_downwards": "ssrd",
}

for month in range(1, 13):
    mm = f"{month:02d}"
    instant_file = cutout_dir / f"{code}_{year}_{mm}_instant.nc"
    accum_file   = cutout_dir / f"{code}_{year}_{mm}_accum.nc"
    out_file     = cutout_dir / f"{code}_{year}_{mm}_merged.nc"

    if not (instant_file.exists() and accum_file.exists()):
        print(f"Skipping month {mm}: Missing files.")
        continue

    ds_inst = xr.open_dataset(instant_file, engine="netcdf4")
    ds_accu = xr.open_dataset(accum_file, engine="netcdf4")
    ds = xr.merge([ds_inst, ds_accu]).load()

    found_rename = {k: v for k, v in rename_map.items() if k in ds}
    ds = ds.rename(found_rename)

    for var in ds.data_vars:
        ds[var].attrs['module'] = 'era5'

    ds.to_netcdf(out_file)
    print(f"Merged: {out_file.name}")
EOF
)

python -c "$PYTHON_CODE"

echo ""
echo "All done. ERA5 cutouts unzipped, renamed, and merged in: $DIR"
