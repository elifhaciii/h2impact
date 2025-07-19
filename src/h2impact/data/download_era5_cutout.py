import argparse
import calendar
from pathlib import Path
import cdsapi
from src.h2impact.constants import PREDEFINED_AREAS, COUNTRY_CODES

def download_era5_cutout(target, variables, area, year, month):
    """
    Download an ERA5 single-level NetCDF cutout via the CDS API for one month.
    """
    c = cdsapi.Client()
    days = [f"{d:02d}" for d in range(1, calendar.monthrange(year, month)[1] + 1)]
    times = [f"{h:02d}:00" for h in range(24)]

    request = {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": variables,
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": times,
        "area": list(area),  # [N, W, S, E]
    }

    print(f"Requesting ERA5 for {year}-{month:02d} over {area}...")
    c.retrieve("reanalysis-era5-single-levels", request, target)
    print(f"Downloaded: {target}")

def parse_args():
    parser = argparse.ArgumentParser(description="Download ERA5 monthly cutouts.")
    parser.add_argument("--year", type=int, required=True, help="Target year (e.g., 2020)")
    parser.add_argument("--region", type=str, choices=PREDEFINED_AREAS.keys(), required=True,
                        help="Country name (e.g., germany, france, poland)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    region = args.region.lower()
    area = PREDEFINED_AREAS[region]
    code = COUNTRY_CODES[region]

    Path("cutouts").mkdir(exist_ok=True)

    variables = [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_temperature",
        "surface_solar_radiation_downwards",
    ]

    for month in range(1, 13):
        target = f"cutouts/{code}_{args.year}_{month:02d}.nc"
        download_era5_cutout(
            target=target,
            variables=variables,
            area=area,
            year=args.year,
            month=month,
        )

