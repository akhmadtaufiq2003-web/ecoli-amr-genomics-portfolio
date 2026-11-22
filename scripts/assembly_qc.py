#!/usr/bin/env python3
"""Calculate transparent descriptive FASTA metrics, without claiming biological QC pass/fail."""
import argparse
import csv
import gzip
import sys
from pathlib import Path


def fasta_lengths_and_bases(path: Path):
    op = gzip.open if str(path).endswith(".gz") else open
    lengths: list[int] = []
    total_gc = total_n = 0
    current_length = 0
    seen_header = False
    with op(path, "rt", encoding="ascii") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if seen_header:
                    if current_length == 0:
                        raise ValueError(f"Empty contig in {path}")
                    lengths.append(current_length)
                seen_header, current_length = True, 0
            else:
                if not seen_header:
                    raise ValueError(f"Sequence before FASTA header: {path}")
                seq = line.upper()
                if any(ch not in "ACGTRYSWKMBDHVN" for ch in seq):
                    raise ValueError(f"Invalid IUPAC nucleotide in {path}")
                total_gc += seq.count("G") + seq.count("C")
                total_n += seq.count("N")
                current_length += len(seq)
    if seen_header:
        if current_length == 0:
            raise ValueError(f"Empty contig in {path}")
        lengths.append(current_length)
    if not lengths:
        raise ValueError(f"No FASTA contigs: {path}")
    return lengths, total_gc, total_n


def metrics(path: Path, sample_id: str | None = None) -> dict:
    lengths, gc, n = fasta_lengths_and_bases(path)
    total = sum(lengths)
    cumulative = 0
    n50 = 0
    for length in sorted(lengths, reverse=True):
        cumulative += length
        if cumulative * 2 >= total:
            n50 = length
            break
    return {
        "sample_id": sample_id or path.name.split(".")[0],
        "contig_count": len(lengths),
        "total_bases": total,
        "n50_bases": n50,
        "gc_percent_total": round(gc / total * 100, 3),
        "n_percent_total": round(n / total * 100, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/assemblies"))
    parser.add_argument("--output", type=Path, default=Path("results/assembly_qc.csv"))
    args = parser.parse_args()
    candidates = sorted(p for p in args.input_dir.iterdir() if p.is_file() and p.name.endswith((".fna", ".fa", ".fasta", ".fna.gz", ".fa.gz", ".fasta.gz"))) if args.input_dir.is_dir() else []
    if not candidates:
        print("ERROR: no assembly FASTA files found; see docs/protocol.md", file=sys.stderr)
        return 2
    try:
        rows = [metrics(p, p.name.removesuffix(".gz").rsplit(".", 1)[0]) for p in candidates]
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Recorded descriptive assembly metrics for {len(rows)} genomes -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
