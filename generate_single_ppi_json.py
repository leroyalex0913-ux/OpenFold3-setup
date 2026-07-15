#!/usr/bin/env python3
"""
csv_to_openfold_json.py

Converts a CSV with columns:
    PDB id, Sequence 1, Sequence 2
into an OpenFold-style input JSON:

{
    "queries": {
        "<PDB id>": {
            "chains": [
                {
                    "molecule_type": "protein",
                    "chain_ids": ["A"],
                    "sequence": "<Sequence 1>"
                },
                {
                    "molecule_type": "protein",
                    "chain_ids": ["B"],
                    "sequence": "<Sequence 2>"
                }
            ]
        },
        ...
    }
}

Usage:
    python csv_to_openfold_json.py input.csv output_directory

The output JSON is written into output_directory, using the same base
name as the input CSV (e.g. "input.csv" -> "output_directory/input.json").
"""

import csv
import json
import os
import sys
import collections


def csv_to_openfold_json(input_csv, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_csv))[0]
    output_json = os.path.join(output_dir, base_name + ".json")
    queries = collections.OrderedDict()

    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)

        required_cols = {"PDB id", "Sequence 1", "Sequence 2"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"CSV is missing required column(s): {', '.join(sorted(missing))}. "
                f"Found columns: {reader.fieldnames}"
            )

        for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header row
            pdb_id = (row.get("PDB id") or "").strip()
            seq1 = (row.get("Sequence 1") or "").strip()
            seq2 = (row.get("Sequence 2") or "").strip()

            if not pdb_id:
                print(f"Warning: row {row_num} has no PDB id, skipping.", file=sys.stderr)
                continue
            if not seq1 or not seq2:
                print(f"Warning: row {row_num} ({pdb_id}) is missing a sequence, skipping.", file=sys.stderr)
                continue

            queries[pdb_id] = {
                "chains": [
                    {
                        "molecule_type": "protein",
                        "chain_ids": ["A"],
                        "sequence": seq1
                    },
                    {
                        "molecule_type": "protein",
                        "chain_ids": ["B"],
                        "sequence": seq2
                    }
                ]
            }

    output = {"queries": queries}

    with open(output_json, "w") as f:
        json.dump(output, f, indent=4)

    print(f"Converted {len(queries)} entries from '{input_csv}' to '{output_json}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_openfold_json.py <input.csv> <output_directory>", file=sys.stderr)
        sys.exit(1)

    csv_to_openfold_json(sys.argv[1], sys.argv[2])
