# src/h2impact/data/download_monthlydata.py

import cdsapi
import zipfile
import xarray as xr
from pathlib import Path
import argparse

def download_era5_cutout(
    target: Path,
    variables: list[str],
    area: tuple[float, float, float, float],
    start_date: str,
    end_date: str,
) -> xr.Dataset:
    """
    Download an ERA5 single‐level NetCDF cutout via the CDS API,
    unzip+merge if necessary, and return it as an xarray.Dataset.
    """
    # make sure the parent folder exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # parse start/end
    year_start, month_start, _ = start_date.split("-")
    _,       month_end,   _ = end_date.split("-")

    # build the list of months from month_start to month_end (inclusive)
    ms = int(month_start)
    me = int(month_end)
    months = [f"{m:02d}" for m in range(ms, me + 1)]

    # days and times
    days  = [f"{d:02d}" for d in range(1, 32)]
    times = [f"{h:02d}:00" for h in range(24)]

    # build the CDS request
    request = {
        "product_type": "reanalysis",
        "format":       "netcdf",
        "variable":     variables,
        "year":         [year_start],
        "month":        months,
        "day":          days,
        "time":         times,
        "area":         list(area),  # [N, W, S, E]
    }

    print(f"→ Requesting ERA5 {start_date}–{end_date} over {area} …")
    c = cdsapi.Client()
    c.retrieve("reanalysis-era5-single-levels", request, str(target))

    # if it came back as a ZIP file, unzip & merge
    if zipfile.is_zipfile(target):
        print("  ↳ got a .zip, unzipping and merging…")
        with zipfile.ZipFile(target) as z:
            z.extractall(target.parent)
            parts = [target.parent / fn for fn in z.namelist() if fn.endswith(".nc")]
        ds = xr.open_mfdataset(parts, combine="by_coords").load()
        ds.to_netcdf(target)      # overwrite the .zip with one .nc
        for p in parts: p.unlink()  
        print("  ↳ unzipped & merged into NetCDF")
    else:
        ds = xr.open_dataset(target, engine="netcdf4")

    print("→ variables:", list(ds.data_vars))
    return ds


def main():
    p = argparse.ArgumentParser(
        description="Download an ERA5 cutout from CDS and merge into one .nc file"
    )
    p.add_argument(
        "-o", "--output", type=Path, default=Path("cutouts/era5.nc"),
        help="where to write the final NetCDF"
    )
    p.add_argument(
        "-s", "--start-date", required=True, metavar="YYYY-MM-DD",
        help="first day (e.g. 2013-05-01)"
    )
    p.add_argument(
        "-e", "--end-date", required=True, metavar="YYYY-MM-DD",
        help="last day  (e.g. 2013-05-31)"
    )
    p.add_argument(
        "--area", type=float, nargs=4, metavar=("N","W","S","E"),
        default=[56.0, 4.0, 46.0, 15.0],
        help="bounding box N W S E"
    )
    args = p.parse_args()

    variables = [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_temperature",
        "surface_solar_radiation_downwards",
    ]

    download_era5_cutout(
        target=args.output,
        variables=variables,
        area=tuple(args.area),
        start_date=args.start_date,
        end_date=args.end_date,
    )


if __name__ == "__main__":
    main()
