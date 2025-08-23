import yaml
import os
import xarray as xr
from pathlib import Path
import sys

# Ensure imports work when run from project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.h2impact.constants import PREDEFINED_AREAS, COUNTRY_CODES

TEMPLATE_PATH = "src/h2impact/configs/config_no_H2_template.yaml"

def main():
    print("---- PyPSA-Eur Scenario Config Generator ----")

    # Step 1: Inputs
    cutout_name = input("Enter cutout name (e.g., de-2020): ").strip()
    cutout_path = input("Enter path to cutout NetCDF file (e.g., cutouts/de-2020-merged.nc): ").strip()
    countries = input("Country name(s) (e.g., germany or 'germany,france'): ").strip().lower().split(",")
    countries = [c.strip() for c in countries if c.strip()]

    iso_codes = []
    bounds = []

    for country in countries:
        if country not in PREDEFINED_AREAS or country not in COUNTRY_CODES:
            raise ValueError(f"Country '{country}' not recognized.")
        bounds.append(PREDEFINED_AREAS[country])
        iso_codes.append(COUNTRY_CODES[country])

    # Use bounding box from the first country
    y_max, x_min, y_min, x_max = bounds[0]

    # Step 2: Read time info from the NetCDF cutout
    try:
        ds = xr.open_dataset(cutout_path)
        try:
            time_coord = ds["time"]
        except KeyError:
            try:
                time_coord = ds["valid_time"]
            except KeyError:
                raise RuntimeError("No 'time' or 'valid_time' coordinate found in NetCDF file.")

        start_time = str(time_coord.values[0])[:10]
        end_time   = str(time_coord.values[-1])[:10]

        ds.close()
    except Exception as e:
        raise RuntimeError(f"Could not read time range from NetCDF: {e}")

    # Step 3: Load template config
    with open(TEMPLATE_PATH, "r") as f:
        config = yaml.safe_load(f)

    # Step 4: Update values
    config["countries"] = iso_codes
    config["snapshots"] = {"start": start_time, "end": end_time}
    
    # Build run.name and run.shared_resources dynamically (e.g., de-2020-noH2)
    run_suffix = f"{iso_codes[0].lower()}-{start_time[:4]}-noH2"
    config["run"]["name"] = run_suffix
    config["run"]["shared_resources"] = run_suffix

    # Atlite cutout definition
    config["atlite"] = {
        "default_cutout": cutout_name,
        "cutouts": {
            cutout_name: {
                "module": "era5",
                "path": cutout_path,
                "x": [x_min, x_max],
                "y": [y_min, y_max],
                "time": [start_time, end_time],
                "variables": ["u10", "v10", "t2m", "si"],
            }
        }
    }

    # Shipdensity disabled
    config["shipdensity"] = {"raster": {"activate": False}}


    # Step 5: Save to yaml_files folder
    yaml_dir = Path("src/h2impact/configs/yaml_files")
    yaml_dir.mkdir(parents=True, exist_ok=True)
    outfile = yaml_dir / f"config_no_H2_{cutout_name}.yaml"

    with open(outfile, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"\n Config file generated at: {outfile.resolve()}")

if __name__ == "__main__":
    main()
