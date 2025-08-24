#!/usr/bin/env python3
"""
Component-Level Cost Analysis for Power System

Usage:
  python plot_cost_summary.py --input costs_2030.csv --output-dir plots/

Dependencies:
  pip install pandas matplotlib
"""

import sys

try:
    import argparse
    import pandas as pd
    import matplotlib.pyplot as plt
    import os
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    print("Install with: pip install pandas matplotlib", file=sys.stderr)
    sys.exit(1)


def plot_and_save(series, title, ylabel, filename, color):
    if series.empty:
        print(f"[!] Skipping {title}: no data available.")
        return
    plt.figure(figsize=(10, 5))
    series.plot(kind="bar", color=color, edgecolor="black")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"[✓] Saved plot: {filename}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot component-level costs from PyPSA cost CSV.")
    parser.add_argument("--input", required=True, help="Path to costs_*.csv file")
    parser.add_argument("--output-dir", default="plots", help="Directory to save plots (default: ./plots)")
    parser.add_argument("--no-save", action="store_true", help="Don't save plots, only print stats")
    args = parser.parse_args()

    # Load CSV
    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Failed to load CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if not {'carrier', 'capital_cost', 'marginal_cost', 'component'}.issubset(df.columns):
        print("CSV must include: carrier, capital_cost, marginal_cost, component", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)
    basename = os.path.basename(args.input).replace(".csv", "")

    # Generator costs
    df_gen = df[df["component"] == "Generator"]
    capital = df_gen.set_index("carrier")["capital_cost"].dropna()
    marginal = df_gen.set_index("carrier")["marginal_cost"].dropna()

    print("\n== Generator Cost Summary ==")
    print("Capital (€):")
    print(capital)
    print("\nMarginal (€/MWh):")
    print(marginal)

    if not args.no_save:
        plot_and_save(capital, "Capital Cost by Generator Carrier", "Capital Cost (€)", f"{args.output_dir}/{basename}_capital_cost.png", "lightblue")
        plot_and_save(marginal, "Marginal Cost by Generator Carrier", "Marginal Cost (€/MWh)", f"{args.output_dir}/{basename}_marginal_cost.png", "salmon")

    # H2-related infra (Store, Link)
    df_h2 = df[df["component"].isin(["Store", "Link"])]
    h2_costs = df_h2.groupby("component")["capital_cost"].sum().rename(index={"Store": "H2 Store", "Link": "H2 Link"})

    print("\n== Hydrogen Infrastructure Capital Cost ==")
    print(h2_costs)

    if not args.no_save and not h2_costs.empty:
        plot_and_save(h2_costs, "Hydrogen Infrastructure Costs", "Capital Cost (€)", f"{args.output_dir}/{basename}_h2_cost.png", "lightgreen")


if __name__ == "__main__":
    main()
