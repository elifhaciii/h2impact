# merge_monthly_cutouts.py

import xarray as xr
from pathlib import Path

cutout_dir = Path(".")  # set to "." if you run the script inside the cutouts folder

# Atlite short variable names
rename_map = {
    "10m_u_component_of_wind":            "u10",
    "10m_v_component_of_wind":            "v10",
    "2m_temperature":                     "t2m",
    "surface_solar_radiation_downwards":  "ssrd",
}

for month in range(1, 13):
    mm = f"{month:02d}"
    instant_file = cutout_dir / f"de-2020-{mm}-instant.nc"
    accum_file   = cutout_dir / f"de-2020-{mm}-accum.nc"
    out_file     = cutout_dir / f"de-2020-{mm}-merged.nc"

    if not (instant_file.exists() and accum_file.exists()):
        print(f"❌ Skipping month {mm}: Missing files.")
        continue

    # Open and merge datasets
    ds_inst = xr.open_dataset(instant_file, engine="netcdf4")
    ds_accu = xr.open_dataset(accum_file,   engine="netcdf4")
    ds = xr.merge([ds_inst, ds_accu]).load()

    # Rename vars
    found_rename = {k: v for k, v in rename_map.items() if k in ds}
    ds = ds.rename(found_rename)

    # Add Atlite "module" metadata
    for var in ds.data_vars:
        ds[var].attrs['module'] = 'era5'

    ds.to_netcdf(out_file)
    print(f"✅ Merged {instant_file.name} + {accum_file.name} → {out_file.name}")

