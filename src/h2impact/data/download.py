import cdsapi
import xarray as xr

def download_era5_cutout(
    target: str,
    variables: list[str],
    area: tuple[float, float, float, float],
    start_date: str,
    end_date: str,
) -> xr.Dataset:
    """
    Download an ERA5 single-level NetCDF cutout via the CDS API and return
    it as an xarray.Dataset.
    """
    c = cdsapi.Client()

    # extract year/month components
    years  = [start_date.split("-")[0]]
    months = [start_date.split("-")[1]]
    # request all days in the month
    days   = [f"{d:02d}" for d in range(1, 32)]
    # request every hour
    times  = [f"{h:02d}:00" for h in range(24)]

    request = {
        "product_type": "reanalysis",
        "format":       "netcdf",
        "variable":     variables,
        "year":         years,
        "month":        months,
        "day":          days,
        "time":         times,
        "area":         list(area),  # [N, W, S, E]
    }

    print(f"Requesting ERA5 for {start_date} to {end_date} over {area}...")
    c.retrieve("reanalysis-era5-single-levels", request, target)
    print("Download complete; now opening with xarray...")

    # explicitly pick the netcdf4 engine
    ds = xr.open_dataset(target, engine="netcdf4")
    print("→ dataset contains variables:", list(ds.data_vars))
    return ds


if __name__ == "__main__":
    # example for May 2013, Belgium
    ds = download_era5_cutout(
        target="cutouts/be-05-2013-era5.nc",
        variables=[
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_temperature",
            "surface_solar_radiation_downwards",
        ],
        area=(56.0, 4.0, 46.0, 15.0),
        start_date="2013-05-01",
        end_date="2013-05-31",
    )
