#!/usr/bin/env python3
"""Validate sample and accession provenance before downloading public genomes."""
import argparse
import csv
import re
import sys
from pathlib import Path

REQUIRED = ("sample_id", "assembly_accession", "bioproject", "source_note")
SAMPLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
ASSEMBLY_RE = re.compile(r"^GC[AF]_[0-9]{9}(?:\.[0-9]+)?$")


def validate_manifest(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"Manifest not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("Manifest is empty or lacks a header")
        missing = set(REQUIRED) - set(reader.fieldnames)
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
        rows = [{k: (v or "").strip() for k, v in row.items() if k is not None}
                for row in reader]
    if not rows:
        raise ValueError("No assemblies selected. Add verified public accessions to data/manifest.csv")
    seen_samples, seen_assemblies = set(), set()
    for line, row in enumerate(rows, start=2):
        sid, accession = row["sample_id"], row["assembly_accession"]
        if not SAMPLE_RE.fullmatch(sid):
            raise ValueError(f"Row {line}: invalid sample_id {sid!r}")
        if not ASSEMBLY_RE.fullmatch(accession):
            raise ValueError(f"Row {line}: invalid NCBI assembly accession {accession!r}")
        if sid in seen_samples or accession in seen_assemblies:
            raise ValueError(f"Row {line}: duplicate sample_id or accession")
        seen_samples.add(sid)
        seen_assemblies.add(accession)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest.csv"))
    parser.add_argument("--accession-output", type=Path, default=Path("data/accessions.txt"))
    args = parser.parse_args()
    try:
        rows = validate_manifest(args.manifest)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    args.accession_output.parent.mkdir(parents=True, exist_ok=True)
    args.accession_output.write_text("\n".join(r["assembly_accession"] for r in rows) + "\n", encoding="utf-8")
    print(f"Validated {len(rows)} assemblies; wrote {args.accession_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
