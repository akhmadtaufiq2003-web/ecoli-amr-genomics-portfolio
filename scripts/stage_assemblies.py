#!/usr/bin/env python3
"""Map NCBI Datasets accession folders to stable sample_id FASTAs."""
import argparse
import shutil
import sys
from pathlib import Path
from validate_manifest import validate_manifest


def stage(manifest: Path, package_dir: Path, output_dir: Path) -> list[Path]:
    rows = validate_manifest(manifest)
    root = package_dir / "ncbi_dataset" / "data"
    plan = []
    for row in rows:
        accession = row["assembly_accession"]
        folder = root / accession
        matches = sorted(folder.glob("*_genomic.fna")) if folder.is_dir() else []
        if len(matches) != 1:
            raise ValueError(f"Expected one genomic FASTA for {accession}, found {len(matches)}")
        plan.append((matches[0], output_dir / f"{row['sample_id']}.fna"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for src, dst in plan:
        shutil.copyfile(src, dst)
    return [dst for _, dst in plan]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=Path("data/manifest.csv"))
    p.add_argument("--package-dir", type=Path, default=Path("data/raw/ncbi_package"))
    p.add_argument("--output-dir", type=Path, default=Path("data/assemblies"))
    a = p.parse_args()
    try:
        paths = stage(a.manifest, a.package_dir, a.output_dir)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Staged {len(paths)} assemblies with manifest sample IDs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
