import yaml
import subprocess
import os

# Path to your template config file
TEMPLATE_PATH = "src/h2impact/configs/config_no_H2_template.yaml"

def main():
    print("---- PyPSA-Eur Scenario Config Generator ----")
    cutout_name = input("Enter cutout name (e.g., de-2024-05): ").strip()
    cutout_path = input("Enter path to cutout NetCDF file: ").strip()
    x_min = float(input("Longitude min (e.g., 4.0): "))
    x_max = float(input("Longitude max (e.g., 15.0): "))
    y_min = float(input("Latitude min (e.g., 46.0): "))
    y_max = float(input("Latitude max (e.g., 56.0): "))
    start_time = input("Start date (YYYY-MM-DD): ").strip()
    end_time = input("End date (YYYY-MM-DD): ").strip()
    country = input("Country code(s) (e.g., DE or 'DE,FR'): ").strip().split(",")
    country = [c.strip() for c in country if c.strip()]

    # Read the template YAML
    with open(TEMPLATE_PATH, "r") as f:
        config = yaml.safe_load(f)

    # Update countries and snapshots if desired
    if country:
        config["countries"] = country
    config["snapshots"] = {"start": start_time, "end": end_time}

    # Update the atlite section
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

    # Always disable shipdensity raster
    config["shipdensity"] = {"raster": {"activate": False}}

    # Ensure configs directory exists
    configs_dir = "src/h2impact/configs"
    os.makedirs(configs_dir, exist_ok=True)

    # Output file path
    outfile = os.path.join(configs_dir, f"config_no_H2_{cutout_name}.yaml")
    with open(outfile, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"\nGenerated config file: {outfile}")

    run = input("Run Snakemake with this config now? [y/N]: ").strip().lower()
    if run == "y":
        snakemake_cmd = [
            "snakemake", "-j1", "--configfile", f"../../{outfile}"
        ]
        print("Running:", " ".join(snakemake_cmd))
        subprocess.run(snakemake_cmd, cwd="external/pypsa-eur")

if __name__ == "__main__":
    main()
