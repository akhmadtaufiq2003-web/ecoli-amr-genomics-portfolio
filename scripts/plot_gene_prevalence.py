#!/usr/bin/env python3
"""Create a figure from an audited AMRFinderPlus sample-level prevalence CSV."""
import argparse
import csv
import sys
from pathlib import Path


def load_rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        needed = {"gene_symbol", "samples_with_gene", "samples_total", "percent_samples"}
        if not reader.fieldnames or not needed.issubset(reader.fieldnames):
            raise ValueError(f"Expected gene_prevalence.csv with {sorted(needed)}")
        rows = []
        for r in reader:
            n, total = int(r["samples_with_gene"]), int(r["samples_total"])
            if not (0 <= n <= total and total > 0):
                raise ValueError("Invalid detection proportions in input")
            p = float(r["percent_samples"])
            if abs(p - n / total * 100) > 0.02:
                raise ValueError("Prevalence column not consistent with count/denominator")
            rows.append((r["gene_symbol"], p, n, total))
    return sorted(rows, key=lambda x: (-x[1], x[0]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=Path("results/summary/gene_prevalence.csv"))
    ap.add_argument("--output", type=Path, default=Path("results/figures/gene_detection_top15.png"))
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    if a.top < 1:
        ap.error("--top must be at least one")
    try:
        rows = load_rows(a.input)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("ERROR: no gene detection data; cannot create a meaningful figure", file=sys.stderr)
        return 2
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("ERROR: install optional matplotlib; see requirements-figures.txt", file=sys.stderr)
        return 2
    selected = rows[:a.top]
    names = [r[0] for r in reversed(selected)]
    values = [r[1] for r in reversed(selected)]
    fig, ax = plt.subplots(figsize=(8.4, max(3.7, len(selected) * 0.35 + 1.3)))
    ax.barh(names, values)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Assemblies with detected AMR gene symbol (%)")
    ax.set_title(f"Detected AMR gene symbols in {selected[0][3]} selected public assemblies")
    fig.tight_layout()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {a.output}; labels represent within-sample-set detection, not population prevalence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
