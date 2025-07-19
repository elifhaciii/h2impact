#!/usr/bin/env python3
"""
Plot H₂ pipeline flows on a Cartopy map with major German city labels for a specified month.

Dependencies (install via pip):
  - pypsa
  - pandas
  - numpy
  - matplotlib
  - cartopy

Required parameters:
  --network NETWORK_PATH   Path to the PyPSA NetCDF network file
  --year YEAR             Year to analyze (e.g., 2020)
  --month MONTH           Month to analyze (1-12)

Optional parameters (with defaults):
  --output OUTPUT_PATH    Output PNG file (default: h2_pipeline_flow.png)
  --pop-threshold N       Minimum city population to label (default: 300000)
  --extent LON_MIN LON_MAX LAT_MIN LAT_MAX
                          Map extent (default: 5 15 47 56)

Example:
  python plot_h2_pipelines_with_cities.py \
    --network base_s_5___2020_full.nc \
    --year 2020 --month 1 \
    --output flow_jan2020.png \
    --pop-threshold 200000 \
    --extent 5 15 47 56
"""
import sys
import argparse
import pypsa
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot H₂ pipeline flows with city labels for a given month."
    )
    parser.add_argument(
        '--network', required=True,
        help='Path to PyPSA NetCDF network file'
    )
    parser.add_argument(
        '--year', type=int, required=True,
        help='Year to analyze (e.g., 2020)'
    )
    parser.add_argument(
        '--month', type=int, choices=range(1,13), required=True,
        help='Month to analyze (1-12)'
    )
    parser.add_argument(
        '--output', default='h2_pipeline_flow.png',
        help='Path for output PNG file'
    )
    parser.add_argument(
        '--pop-threshold', type=int, default=300000,
        help='Minimum city population to label'
    )
    parser.add_argument(
        '--extent', nargs=4, type=float, metavar=('lon_min','lon_max','lat_min','lat_max'),
        default=[5,15,47,56],
        help='Map extent: lon_min lon_max lat_min lat_max'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        network = pypsa.Network(args.network)
    except Exception as e:
        print(f"Error loading network: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter pipeline links
    mask = network.links.carrier.str.contains('pipeline', case=False, na=False)
    pipelines = network.links.loc[mask].copy()

    # Compute monthly flows
    flows = network.links_t.p0
    mask_time = (flows.index.year == args.year) & (flows.index.month == args.month)
    flows_sum = flows.loc[mask_time].abs().sum(axis=0)
    flows_sum.name = 'total_flow_MWh'
    pipelines = pipelines.join(flows_sum, how='left').fillna(0)

    # Compute line widths (2-8)
    vmax = pipelines.total_flow_MWh.max()
    if vmax <= 0:
        widths = np.full(len(pipelines), 2.0)
    else:
        widths = 2.0 + 6.0 * (pipelines.total_flow_MWh / vmax)

    # Setup map
    fig, ax = plt.subplots(
        figsize=(8,6), subplot_kw=dict(projection=ccrs.PlateCarree())
    )
    ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=0)
    ax.add_feature(cfeature.COASTLINE, zorder=1)

    # Colormap
    cmap = plt.cm.Blues
    norm = plt.Normalize(vmin=0, vmax=max(vmax,1e-6))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Plot pipelines
    for (_, link), lw in zip(pipelines.iterrows(), widths):
        b0 = network.buses.loc[link.bus0]
        b1 = network.buses.loc[link.bus1]
        ax.plot(
            [b0.x, b1.x], [b0.y, b1.y],
            linewidth=lw,
            color=cmap(norm(link.total_flow_MWh)),
            transform=ccrs.PlateCarree(), solid_capstyle='round', alpha=0.8
        )

    # Plot cities above threshold
    shpfile = shpreader.natural_earth(
        resolution='10m', category='cultural', name='populated_places'
    )
    for record in shpreader.Reader(shpfile).records():
        attrs = record.attributes
        if attrs.get('ADM0NAME') == 'Germany' and attrs.get('POP_MAX',0) >= args.pop_threshold:
            lon, lat = record.geometry.x, record.geometry.y
            ax.plot(lon, lat, marker='o', markersize=3,
                    color='orange', transform=ccrs.PlateCarree(), zorder=5)
            ax.text(lon+0.1, lat+0.1, attrs.get('NAME'),
                    fontsize=6, color='brown', transform=ccrs.PlateCarree(), zorder=5)

    # Finalize map
    ax.set_extent(args.extent, crs=ccrs.PlateCarree())
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label(f'Total H₂ pipeline flow (MWh) — {args.year}-{args.month:02d}')
    ax.set_title(f'Aggregate H₂ Pipeline Flow — {args.year}-{args.month:02d}')

    plt.tight_layout()
    fig.savefig(args.output, dpi=300, bbox_inches='tight')
    print(f"Map saved to {args.output}")
    plt.show()

if __name__ == '__main__':
    main()

