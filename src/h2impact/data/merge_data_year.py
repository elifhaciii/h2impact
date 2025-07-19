import xarray as xr
from pathlib import Path

# List your 12 merged monthly files
files = [Path(f"de-2020-{month:02d}-merged.nc") for month in range(1, 13)]

# Sanity check: print out any files that do NOT exist
for f in files:
    if not f.exists():
        print(f"❌ Missing file: {f}")

# Merge the files into a single dataset
ds = xr.open_mfdataset([str(f) for f in files], combine="by_coords", engine="netcdf4")
ds.load()

# Save the merged yearly dataset
out = Path("de-2020-merged-year.nc")
if out.exists():
    out.unlink()
ds.to_netcdf(out)

print(f"✅ Merged yearly NetCDF written to: {out}")


