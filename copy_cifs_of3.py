#!/usr/bin/env python3
"""
copy_best_cifs.py

For each protein-pair directory under a root directory, this script:
  1. Recursively finds every "*_confidences_aggregated.json" file
     (these live inside the 5 seed subdirectories, one per sample).
  2. Reads the "sample_ranking_score" field from each one.
  3. Determines which sample (across all seeds) has the highest score.
  4. Copies ONLY that sample's .cif model file (named like
     "<name>_seed_<seed>_sample_<n>_model.cif") into a single,
     separate output directory (not back into the protein pair dir).

Works for any number of protein-pair directories and seed directories.

Usage:
    python copy_best_cifs.py /path/to/root_dir /path/to/output_dir
    python copy_best_cifs.py /path/to/root_dir /path/to/output_dir --dry-run
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

AGG_SUFFIX = "_confidences_aggregated.json"
CIF_SUFFIX = "_model.cif"


def find_stem(agg_file: Path) -> str:
    """
    Derive the shared filename prefix ("stem") for a sample from its
    aggregated-confidences filename, e.g.:
        21IE_seed_1181241943_sample_1_confidences_aggregated.json
    -> 21IE_seed_1181241943_sample_1
    """
    name = agg_file.name
    if name.endswith(AGG_SUFFIX):
        return name[: -len(AGG_SUFFIX)]
    return agg_file.stem


def process_protein_pair_dir(pair_dir: Path, output_dir: Path, dry_run: bool = False):
    agg_files = list(pair_dir.rglob(f"*{AGG_SUFFIX}"))

    if not agg_files:
        print(f"  [skip] No confidences_aggregated.json files found in {pair_dir}")
        return

    best_file = None
    best_score = None

    for agg_file in agg_files:
        try:
            with open(agg_file, "r") as f:
                data = json.load(f)
            score = data.get("sample_ranking_score")
            if score is None:
                print(f"  [warn] 'sample_ranking_score' missing in {agg_file}, skipping")
                continue
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [warn] Could not read {agg_file}: {e}")
            continue

        if best_score is None or score > best_score:
            best_score = score
            best_file = agg_file

    if best_file is None:
        print(f"  [skip] No valid sample_ranking_score found in {pair_dir}")
        return

    stem = find_stem(best_file)
    cif_file = best_file.parent / f"{stem}{CIF_SUFFIX}"

    print(f"  Best sample: {best_file.relative_to(pair_dir)}  (score={best_score})")

    if not cif_file.exists():
        print(f"  [warn] Expected .cif file not found: {cif_file}")
        return

    dest = output_dir / cif_file.name
    print(f"  Copying: {cif_file} -> {dest}")
    if not dry_run:
        shutil.copy2(cif_file, dest)


def main():
    parser = argparse.ArgumentParser(description="Copy the best-scoring .cif model file from each protein pair directory into a new output directory.")
    parser.add_argument("root_dir", help="Path to the root directory containing protein pair directories")
    parser.add_argument("output_dir", help="Path to the directory where winning .cif files will be copied")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied without actually copying")
    args = parser.parse_args()

    root = Path(args.root_dir)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    pair_dirs = sorted(d for d in root.iterdir() if d.is_dir())

    if not pair_dirs:
        print(f"No subdirectories found in {root}")
        sys.exit(0)

    print(f"Found {len(pair_dirs)} protein pair directories under {root}")
    print(f"Output directory: {output_dir}\n")

    for pair_dir in pair_dirs:
        print(f"Processing: {pair_dir.name}")
        process_protein_pair_dir(pair_dir, output_dir, dry_run=args.dry_run)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
