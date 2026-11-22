#!/usr/bin/env python3
"""Summarize AMRFinderPlus determinants, separating genes from point mutations.

Both recent ('Element symbol') and older ('Gene symbol') output headers are accepted.
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


def parse_report(path: Path) -> dict:
    """Read one report; count hits and distinct symbols, without phenotype prediction."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = set(reader.fieldnames or [])
        symbol_field = next((k for k in ("Element symbol", "Gene symbol") if k in fields), None)
        if not symbol_field or not {"Element type", "Element subtype"}.issubset(fields):
            raise ValueError(f"{path}: missing AMRFinderPlus fields (symbol/type/subtype)")
        gene_hits = mutation_hits = 0
        genes: set[str] = set()
        mutations: set[str] = set()
        subtypes = Counter()
        for row in reader:
            if (row.get("Element type") or "").strip().upper() != "AMR":
                continue
            symbol = (row.get(symbol_field) or "").strip()
            if not symbol or symbol == "-":
                continue
            subtype = (row.get("Element subtype") or "").strip().upper()
            if subtype.startswith("POINT"):
                mutation_hits += 1
                mutations.add(symbol)
            else:
                gene_hits += 1
                genes.add(symbol)
            subtypes[subtype or "(not specified)"] += 1
    return {"gene_hits": gene_hits, "mutation_hits": mutation_hits,
            "genes": genes, "mutations": mutations, "subtypes": subtypes}


def aggregate(paths: list[Path]) -> dict[str, dict]:
    if not paths:
        raise ValueError("No per-sample AMRFinderPlus TSV reports found")
    out = {}
    for path in paths:
        sample = path.stem
        if sample in out:
            raise ValueError(f"Duplicate sample ID: {sample}")
        out[sample] = parse_report(path)
    return out


def write_reports(data: dict[str, dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "sample_amr_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", "amr_gene_hits", "unique_amr_gene_symbols", "amr_point_mutation_hits", "unique_point_mutation_symbols"])
        for sample, row in sorted(data.items()):
            writer.writerow([sample, row["gene_hits"], len(row["genes"]), row["mutation_hits"], len(row["mutations"])])
    symbols = sorted(set().union(*(r["genes"] for r in data.values())))
    with (output_dir / "gene_presence_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", *symbols])
        for sample, row in sorted(data.items()):
            writer.writerow([sample, *(int(symbol in row["genes"]) for symbol in symbols)])
    with (output_dir / "gene_prevalence.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["gene_symbol", "samples_with_gene", "samples_total", "percent_samples"])
        for symbol in symbols:
            n = sum(symbol in row["genes"] for row in data.values())
            writer.writerow([symbol, n, len(data), f"{100*n/len(data):.2f}"])
    muts = sorted(set().union(*(r["mutations"] for r in data.values())))
    with (output_dir / "point_mutation_presence_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", *muts])
        for sample, row in sorted(data.items()):
            writer.writerow([sample, *(int(symbol in row["mutations"]) for symbol in muts)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("results/amrfinder"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/summary"))
    args = parser.parse_args()
    try:
        paths = sorted(args.input_dir.glob("*.tsv")) if args.input_dir.is_dir() else []
        data = aggregate(paths)
        write_reports(data, args.output_dir)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Summary created for {len(data)} samples at {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
