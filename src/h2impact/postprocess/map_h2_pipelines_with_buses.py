#!/usr/bin/env python3
"""
Map H₂ pipeline network with pipeline capacities and electrolysis bus locations via CLI.

Dependencies:
  pip install pypsa pandas numpy matplotlib cartopy

Usage:
  python map_h2_pipelines_with_buses.py \
    --network base_s_5___2020_full.nc \
    --year 2020 --month 1 \
    [--output h2_pipeline_with_buses.png] \
    [--extent 5 15 47 56] [--top-n-buses 10]
"""
import argparse
import pypsa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def parse_args():
    parser = argparse.ArgumentParser(
        description="Map H₂ pipelines with pipeline capacities and overlay electrolysis bus points."
    )
    parser.add_argument(
        '--network', required=True,
        help='Path to PyPSA NetCDF network file'
    )
    parser.add_argument(
        '--year', type=int, required=True,
        help='Year of flows to compute (e.g., 2020)'
    )
    parser.add_argument(
        '--month', type=int, choices=range(1,13), required=True,
        help='Month of flows to compute (1-12)'
    )
    parser.add_argument(
        '--output', default='h2_pipeline_with_buses.png',
        help='Output PNG file name'
    )
    parser.add_argument(
        '--extent', nargs=4, type=float, metavar=('lon_min','lon_max','lat_min','lat_max'),
        default=[5,15,47,56],
        help='Map extent: lon_min lon_max lat_min lat_max'
    )
    parser.add_argument(
        '--top-n-buses', type=int, default=10,
        help='Number of top electrolysis buses to label'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    # assign
    network_path = args.network
    year = args.year
    month = args.month
    output_path = args.output
    extent = args.extent
    top_n_buses = args.top_n_buses

    n = pypsa.Network(network_path)

    # print all buses
    print("All buses in the network with coordinates:")
    print(n.buses[['x','y']])

    # 1) pipelines
    mask_pipe = n.links.carrier.str.contains("pipeline", case=False, na=False)
    pipes = n.links.loc[mask_pipe, ["bus0","bus1","p_nom_opt"]].copy()
    pipes.rename(columns={"p_nom_opt":"capacity_MW"}, inplace=True)
    vmax = pipes.capacity_MW.max()
    widths = 1.0 + 4.0 * (pipes.capacity_MW / vmax) if vmax>0 else np.full(len(pipes),1.0)
    cmap_pipe = plt.cm.viridis
    norm_pipe = plt.Normalize(vmin=0, vmax=vmax)

    # 2) electrolysis summary
    flows = n.links_t.p0
    mask_time = (flows.index.year==year)&(flows.index.month==month)
    flows_mth = flows.loc[mask_time]

    elec_mask = n.links.carrier.str.contains("Electrolysis", case=False, na=False)
    elec_links = n.links.loc[elec_mask]
    energy_in_link = flows_mth[elec_links.index].abs().sum(axis=0)

    # efficiencies
    elec_eff = elec_links.efficiency.mean() if 'efficiency' in elec_links else 1.0
    fc_mask = n.links.carrier.str.contains("Fuel Cell", case=False, na=False)
    fc_eff = n.links.loc[fc_mask,'efficiency'].mean() if fc_mask.any() else 1.0
    rt_eff = elec_eff * fc_eff

    df_bus = pd.DataFrame({ 'bus':elec_links.bus0.values, 'energy_in_MWh':energy_in_link.values })
    summary = df_bus.groupby('bus',as_index=False).sum()
    summary['potential_out_MWh'] = summary['energy_in_MWh'] * rt_eff
    summary['x'] = summary['bus'].map(n.buses['x'])
    summary['y'] = summary['bus'].map(n.buses['y'])
    top_buses = summary.nlargest(top_n_buses, 'potential_out_MWh')

    # 3) plot
    fig, ax = plt.subplots(figsize=(10,8), subplot_kw=dict(projection=ccrs.PlateCarree()))
    ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=0)
    ax.add_feature(cfeature.COASTLINE, zorder=1)

    for (_,link), lw in zip(pipes.iterrows(),widths):
        b0=n.buses.loc[link.bus0]; b1=n.buses.loc[link.bus1]
        ax.plot([b0.x,b1.x],[b0.y,b1.y], linewidth=lw,
                color=cmap_pipe(norm_pipe(link.capacity_MW)),
                transform=ccrs.PlateCarree(), solid_capstyle='round', alpha=0.7)

    sizes = (summary.energy_in_MWh/summary.energy_in_MWh.max())*100
    cmap_bus = plt.cm.hot
    norm_bus = plt.Normalize(vmin=0, vmax=summary.potential_out_MWh.max())
    ax.scatter(summary['x'],summary['y'], s=sizes, c=summary['potential_out_MWh'],
               cmap=cmap_bus, norm=norm_bus, transform=ccrs.PlateCarree(),
               edgecolor='k', linewidth=0.5, zorder=5)
    for _,row in top_buses.iterrows():
        ax.text(row['x']+0.1,row['y']+0.1, row['bus'], fontsize=8,
                transform=ccrs.PlateCarree(), zorder=6)

    ax.set_extent(extent, crs=ccrs.PlateCarree())
    tbp = plt.cm.ScalarMappable(cmap=cmap_pipe,norm=norm_pipe); tbp.set_array([])
    cbar1=fig.colorbar(tbp,ax=ax,orientation='vertical',pad=0.02); cbar1.set_label('Pipeline capacity (MW)')
    tbb = plt.cm.ScalarMappable(cmap=cmap_bus,norm=norm_bus); tbb.set_array([])
    cbar2=fig.colorbar(tbb,ax=ax,orientation='horizontal',pad=0.02,aspect=40); cbar2.set_label('Potential H₂ reconversion (MWh)')
    ax.set_title(f'H₂ Pipelines & Electrolysis Buses — {year}-{month:02d}')
    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    print(f"Map saved to {output_path}")
    plt.show()

if __name__=='__main__':
    main()

