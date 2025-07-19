#!/usr/bin/env python3
"""
Compute H₂ round-trip conversion metrics with descriptive CLI parameters.

Dependencies:
  pip install pypsa pandas
Usage:
  python calculate_h2_conversion_potential.py \
    --input base_s_5___2020_full.nc \
    --year 2020 --month 1 \
    --output summary.csv
"""
import sys

# Check dependencies
try:
    import argparse
    import pypsa
    import pandas as pd
except ImportError as e:
    missing = e.name if hasattr(e, 'name') else str(e)
    print(f"Error: missing dependency '{missing}'.", file=sys.stderr)
    print("Install required packages with: pip install pypsa pandas", file=sys.stderr)
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute theoretical and empirical H₂ conversion metrics for a given month from a PyPSA network."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the PyPSA NetCDF network file"
    )
    parser.add_argument(
        "--year", type=int, required=True,
        help="Analysis year, e.g. 2020"
    )
    parser.add_argument(
        "--month", type=int, choices=range(1,13), required=True,
        help="Analysis month (1-12)"
    )
    parser.add_argument(
        "--output",
        help="Path for CSV summary output (default: h2_conversion_summary_YEAR_MONTH.csv)"
    )
    parser.add_argument(
        "--no-csv", action="store_true",
        help="Skip CSV export"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    n = pypsa.Network(args.input)
    flows = n.links_t.p0
    mask = (flows.index.year == args.year) & (flows.index.month == args.month)
    flows_mth = flows.loc[mask]

    elec_mask = n.links.carrier.str.contains("Electrolysis", case=False, na=False)
    fc_mask   = n.links.carrier.str.contains("Fuel Cell", case=False, na=False)

    energy_in  = flows_mth.loc[:, elec_mask].abs().sum().sum()
    energy_out = flows_mth.loc[:, fc_mask].abs().sum().sum()

    elec_eff = n.links.loc[elec_mask, "efficiency"].mean() or 0.0
    fc_eff   = n.links.loc[fc_mask,   "efficiency"].mean() or 0.0

    h2_energy        = energy_in * elec_eff
    potential_output = h2_energy * fc_eff
    theoretical_rt   = elec_eff * fc_eff

    empirical_rt = energy_out / energy_in if energy_in else 0.0

    fmt_mwh = lambda x: f"{x:,.1f} MWh"
    fmt_pct = lambda x: f"{100*x:.1f}%"

    period = f"{args.year}-{args.month:02d}"
    print(f"Analysis Period: {period}\n")
    print(f"Electrolysis input:            {fmt_mwh(energy_in)}")
    print(f"Actual fuel-cell output:        {fmt_mwh(energy_out)}")
    print(f"Nominal electrolyzer eff.:      {fmt_pct(elec_eff)}")
    print(f"Nominal fuel-cell eff.:         {fmt_pct(fc_eff)}")
    print(f"Theoretical H₂ stored energy:   {fmt_mwh(h2_energy)}")
    print(f"Theoretical electricity output: {fmt_mwh(potential_output)}")
    print(f"Theoretical round-trip eff.:    {fmt_pct(theoretical_rt)}")
    print(f"Empirical round-trip eff.:      {fmt_pct(empirical_rt)}")

    if not args.no_csv:
        df = pd.DataFrame({
            "energy_in": [energy_in],
            "energy_out": [energy_out],
            "elec_eff": [elec_eff],
            "fc_eff": [fc_eff],
            "h2_energy": [h2_energy],
            "potential_output": [potential_output],
            "theoretical_rt": [theoretical_rt],
            "empirical_rt": [empirical_rt]
        }, index=[period])
        out_path = args.output or f"h2_conversion_summary_{period}.csv"
        try:
            df.to_csv(out_path)
            print(f"Summary exported to {out_path}")
        except Exception as e:
            print(f"CSV export failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

