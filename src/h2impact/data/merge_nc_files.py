import xarray as xr
from pathlib import Path
import argparse
import sys

def is_valid_nc(nc_path):
    try:
        with xr.open_dataset(nc_path) as ds:
            ds.load()
        return True
    except Exception as e:
        print(f"[WARN] Skipping invalid file: {nc_path} ({e})")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Merge NetCDF files along time dimension, user-friendly."
    )
    parser.add_argument(
        "-i", "--input-folder", type=str, default="tmp_monthly_nc",
        help="Folder with monthly .nc files"
    )
    parser.add_argument(
        "-o", "--output-file", type=str, default="merged_selected.nc",
        help="Output .nc filename"
    )
    parser.add_argument(
        "--months", nargs="*", type=int,
        help="List of months to merge (e.g. --months 1 2 3)"
    )
    parser.add_argument(
        "--files", nargs="*", type=str,
        help="Specific filenames to merge (overrides --months)"
    )
    args = parser.parse_args()

    input_folder = Path(args.input_folder)

    if args.files:
        nc_files = [Path(f) for f in args.files]
    elif args.months:
        # Select files whose month matches any given in --months
        nc_files = [
            f for f in sorted(input_folder.glob("*.nc"))
            if int(f.stem.split('-')[1]) in args.months
        ]
    else:
        nc_files = sorted(input_folder.glob("*.nc"))

    valid_files = [str(f) for f in nc_files if is_valid_nc(f)]
    if not valid_files:
        print("No valid .nc files to merge.")
        sys.exit(1)

    print(f"Merging {len(valid_files)} files:")
    for f in valid_files:
        print(f"  {f}")
    ds_merged = xr.open_mfdataset(valid_files, combine="by_coords")
    ds_merged.to_netcdf(args.output_file)
    print(f"Successfully merged to: {args.output_file}")

if __name__ == "__main__":
    main()
