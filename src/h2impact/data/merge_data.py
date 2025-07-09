# Revised merge_cutout.py

import xarray as xr
from pathlib import Path
import sys

# 1) Define prefix & paths
prefix = "be-05-2013-era5"
cutout_dir = Path("cutouts")
instant_file = cutout_dir / "data_stream-oper_stepType-instant.nc"
accum_file   = cutout_dir / "data_stream-oper_stepType-accum.nc"

# 2) Check existence
for f in (instant_file, accum_file):
    if not f.exists():
        print(f"❌ Missing expected file: {f}", file=sys.stderr)
        sys.exit(1)

# 3) Open & merge
ds_inst = xr.open_dataset(instant_file, engine="netcdf4")
ds_accu = xr.open_dataset(accum_file,   engine="netcdf4")
ds = xr.merge([ds_inst, ds_accu]).load()

# 4) Swap/rename time axis
if "valid_time" in ds.dims:
    ds = ds.swap_dims({"valid_time": "time"})
if "valid_time" in ds.coords:
    ds = ds.rename({"valid_time": "time"})

# 5) Inspect variables
print("🔍 Merged dataset variables:", list(ds.data_vars))

# 6) Atlite rename map
rename_map = {
    "10m_u_component_of_wind":            "u10",
    "10m_v_component_of_wind":            "v10",
    "2m_temperature":                     "t2m",
    "surface_solar_radiation_downwards":  "si",
    # add more mappings if your dataset has extra fields
}

# 7) Warn about any vars without a mapping
unmapped = set(ds.data_vars) - set(rename_map.keys())
if unmapped:
    print("⚠️ Unmapped variables present:", unmapped)

# 8) Rename only those found
ds = ds.rename({orig: short for orig, short in rename_map.items() if orig in ds.data_vars})

# 8.5) Attach Atlite 'module' metadata so `atlite.Cutout` can recognize each variable
for var in ds.data_vars:
    ds[var].attrs['module'] = 'era5'

# 9) Write out
out = cutout_dir / f"{prefix}.nc"
if out.exists():
    out.unlink()
ds.to_netcdf(out)

print(f"✅ Merged & renamed cutout written to: {out}")
print("Final dims:", ds.dims)
print("Final data_vars and modules:")
for var in ds.data_vars:
    print(" ", var, "→ module:", ds[var].attrs.get('module'))
