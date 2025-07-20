#!/usr/bin/env python3
"""
Capacity-Factor Analysis of Electrolysers with Dispatch Constraints (CLI)

Dependencies:
  pip install pypsa numpy matplotlib

Usage:
  python capacity_factor_analysis_cli.py \
    --network base_s_5___2020_full.nc \
    --year 2020 --month 1 \
    --price-threshold 50.0 \
    --min-turndown 0.4 \
    --outage-fraction 0.05 \
    [--histogram cf_hist.png] [--boxplot cf_box.png]
"""
import argparse
import sys
import numpy as np
import pypsa
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(
        description='Compute electrolyser capacity factors with realistic dispatch constraints.'
    )
    parser.add_argument('--network', '-n', required=True,
                        help='Path to PyPSA NetCDF network file')
    parser.add_argument('--year', '-y', type=int, required=True,
                        help='Year of analysis, e.g. 2020')
    parser.add_argument('--month', '-m', type=int, choices=range(1,13), required=True,
                        help='Month of analysis (1-12)')
    parser.add_argument('--price-threshold', type=float, default=50.0,
                        help='€/MWh threshold to run electrolysers')
    parser.add_argument('--min-turndown', type=float, default=0.4,
                        help='Minimum fraction of p_nom when running')
    parser.add_argument('--outage-fraction', type=float, default=0.05,
                        help='Fraction of hours in random outage')
    parser.add_argument('--histogram', 
                        help='Path to save capacity factor histogram PNG')
    parser.add_argument('--boxplot', 
                        help='Path to save capacity factor boxplot PNG')
    return parser.parse_args()


def main():
    args = parse_args()
    # Load network
    try:
        net = pypsa.Network(args.network)
    except Exception as e:
        print(f"Error loading network: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract monthly flows
    flows = net.links_t.p0
    mask_time = (flows.index.year == args.year) & (flows.index.month == args.month)
    flows_mth = flows.loc[mask_time]
    hours = len(flows_mth) or 1

    # Identify electrolysis links
    elec_mask = net.links.carrier.str.contains('Electrolysis', case=False, na=False)
    elec_links = net.links[elec_mask]
    if elec_links.empty:
        print("No electrolyser links found.")
        sys.exit(0)

    p_nom = elec_links.p_nom_opt.fillna(0)

    # Simulate prices (or use actual if available)
    try:
        prices = net.generators_t.marginal_price.loc[mask_time]
    except Exception:
        t = hours
        prices = 40 + 20 * np.sin(2 * np.pi * np.arange(t) / 24)

    # Dispatch mask
    run_mask = prices >= args.price_threshold
    rng = np.random.default_rng(seed=42)
    outages = rng.choice(hours, size=int(hours * args.outage_fraction), replace=False)
    run_mask.iloc[outages] = False

    # Raw dispatch flows
    raw = flows_mth[elec_links.index].abs()
    # Apply run mask
    disp = raw.where(run_mask, 0.0)
    # Enforce minimum turndown
    floor = p_nom * args.min_turndown
    disp = disp.where(disp >= floor, 0.0)

    # Capacity factors
    cf_raw = raw.sum(axis=0) / (p_nom * hours)
    cf_constrained = disp.sum(axis=0) / (p_nom * hours)

    # Summary
    print(f"Raw CF ({args.year}-{args.month:02d}):   Min {cf_raw.min():.2%}, Max {cf_raw.max():.2%}, Mean {cf_raw.mean():.2%}")
    print(f"Constr CF: Min {cf_constrained.min():.2%}, Max {cf_constrained.max():.2%}, Mean {cf_constrained.mean():.2%}\n")

    # Plot histogram
    plt.figure()
    plt.hist(cf_raw.dropna(), bins=20, alpha=0.6, label='Raw')
    plt.hist(cf_constrained.dropna(), bins=20, alpha=0.6, label='Constrained')
    plt.xlabel('Capacity Factor')
    plt.ylabel('Number of Links')
    plt.legend()
    plt.title(f'CF Distribution Raw vs Constrained ({args.year}-{args.month:02d})')
    plt.tight_layout()
    if args.histogram:
        plt.savefig(args.histogram, dpi=300)
        print(f"Histogram saved to {args.histogram}")
    else:
        plt.show()

    # Plot boxplot
    plt.figure()
    plt.boxplot([cf_raw.dropna(), cf_constrained.dropna()], labels=['Raw','Constrained'], vert=False)
    plt.xlabel('Capacity Factor')
    plt.title('CF Boxplot Raw vs Constrained')
    plt.tight_layout()
    if args.boxplot:
        plt.savefig(args.boxplot, dpi=300)
        print(f"Boxplot saved to {args.boxplot}")
    else:
        plt.show()

if __name__ == '__main__':
    main()

