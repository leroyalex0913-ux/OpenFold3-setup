#!/usr/bin/env python3
"""
copy_best_samples.py

For each protein-pair directory under a root directory, this script:
  1. Recursively finds every "*_confidences_aggregated.json" file
     (these live inside the 5 seed subdirectories, one per sample).
  2. Reads the "sample_ranking_score" field from each one.
  3. Determines which sample (across all seeds) has the highest score.
  4. Copies all files belonging to that winning sample (identified by
     shared filename prefix, e.g. "<name>_seed_<seed>_sample_<n>_")
     directly into the protein-pair directory.

Works for any number of protein-pair directories, any number of seed
directories, and any number of files per sample (as long as they share
the same filename prefix as the aggregated-confidences file).

Usage:
    python copy_best_samples.py /path/to/root_dir
    python copy_best_samples.py /path/to/root_dir --dry-run
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

AGG_SUFFIX_MARKERS = ["_confidences_aggregated.json"]


def find_stem(agg_file: Path) -> str:
    """
    Derive the shared filename prefix ("stem") for a sample from its
    aggregated-confidences filename, e.g.:
        21IE_seed_1181241943_sample_1_confidences_aggregated.json
    -> 21IE_seed_1181241943_sample_1
    """
    name = agg_file.name
    for marker in AGG_SUFFIX_MARKERS:
        if name.endswith(marker):
            return name[: -len(marker)]
    # Fallback: strip the .json extension only
    return agg_file.stem


def find_sibling_files(agg_file: Path, stem: str):
    """Return all files in the same directory that share the sample's stem."""
    return sorted(f for f in agg_file.parent.iterdir()
                  if f.is_file() and f.name.startswith(stem))


def process_protein_pair_dir(pair_dir: Path, dry_run: bool = False):
    agg_files = list(pair_dir.rglob("*_confidences_aggregated.json"))

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
    siblings = find_sibling_files(best_file, stem)

    print(f"  Best sample: {best_file.relative_to(pair_dir)}  (score={best_score})")
    print(f"  Files to copy ({len(siblings)}):")
    for src in siblings:
        dest = pair_dir / src.name
        print(f"    {src.relative_to(pair_dir)} -> {dest.relative_to(pair_dir)}")
        if not dry_run:
            shutil.copy2(src, dest)


def main():
    parser = argparse.ArgumentParser(description="Copy best-scoring sample files into each protein pair directory.")
    parser.add_argument("root_dir", help="Path to the root directory containing protein pair directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied without actually copying")
    args = parser.parse_args()

    root = Path(args.root_dir)
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    pair_dirs = sorted(d for d in root.iterdir() if d.is_dir())

    if not pair_dirs:
        print(f"No subdirectories found in {root}")
        sys.exit(0)

    print(f"Found {len(pair_dirs)} protein pair directories under {root}\n")

    for pair_dir in pair_dirs:
        print(f"Processing: {pair_dir.name}")
        process_protein_pair_dir(pair_dir, dry_run=args.dry_run)
        print()

    print("Done.")


if __name__ == "__main__":
    main()