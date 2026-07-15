# OpenFold3 Workflow

This repository contains the scripts and configuration used to run protein–protein interaction (PPI) predictions with [OpenFold3](https://github.com/aqlaboratory/openfold-3) on the HPC cluster, plus post-processing scripts to pull out the best-scoring models.

## Contents

| File | Purpose |
|---|---|
| [`generate_single_ppi_json.py`](./generate_single_ppi_json.py) | Converts a CSV of protein pairs into an OpenFold3 input JSON |
| [`run_openfold.slurm`](./run_openfold.slurm) | SLURM batch script that runs OpenFold3 predictions on a GPU node |
| [`copy_best_rs_of3.py`](./copy_best_rs_of3.py) | Copies the highest-ranking-score sample's files into each pair's output directory |
| [`copy_cifs_of3.py`](./copy_cifs_of3.py) | Copies only the highest-ranking-score `.cif` model for each pair into one combined directory |

---

## Prerequisites

- OpenFold3 supports Python 3.10–3.13.
- Log in to a GPU dev node before making predictions.

### Install pixi

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

### Clone and install OpenFold3

```bash
git clone https://github.com/aqlaboratory/openfold-3.git
pixi install -e openfold3-cuda12
```

OpenFold3 is already cloned and installed in the lab's shared research directory `/mnt/research/woldring-lab/openfold-3` other users do **not** need to re-clone or re-run `pixi install` — they can use the existing environment directly, as long as they have read/execute permissions on that directory and `pixi` (or the appropriate module) available in their own environment.

### Set up OpenFold3

```bash
pixi run -e openfold3-cpu setup_openfold
```

---

## 1. Build the input JSON

OpenFold3 supports more than two-protein interactions (non-protein binders, more than two chains, etc.). [`generate_single_ppi_json.py`](./generate_single_ppi_json.py) as written only handles the **2-protein-chain** case, and will need editing to support other input types. Full details on the input JSON schema are in the [OpenFold3 input format reference](https://openfold-3.readthedocs.io/en/latest/input_format_reference.html).

**To use the script as-is:**

1. Create a CSV with exactly these three column headers (case-sensitive):

   | PDB id | Sequence 1 | Sequence 2 |
   |---|---|---|
   | 21IE | `MKT...` | `GHV...` |

2. Generate the input JSON:

   ```bash
   python3 generate_single_ppi_json.py input.csv /path/to/output_directory
   ```

   | Parameter | Description |
   |---|---|
   | `input.csv` | CSV file with `PDB id`, `Sequence 1`, `Sequence 2` columns |
   | `output_directory` | Directory to write the resulting `<input>.json` file into |

---

## 2. Run OpenFold3

Predictions are launched via [`run_openfold.slurm`](./run_openfold.slurm). Before submitting, update:

- `#SBATCH --output=` and `#SBATCH --error=` — your own log paths
- `--query-json` — path to the input JSON from step 1
- `--output-dir` — path to your desired output directory

`run_openfold predict` supports additional optional parameters (number of samples, inference checkpoint, etc.) — see the [OpenFold3 inference docs](https://openfold-3.readthedocs.io/en/latest/inference.html) for the full list.

Submit with:

```bash
sbatch run_openfold.slurm
```

---

## 3. Collect the best-scoring models

Once a run finishes, use one of the two copy scripts depending on what you need:

### Option A — Keep all files for the winning sample, per pair

[`copy_best_rs_of3.py`](./copy_best_rs_of3.py) finds, for each protein-pair output directory, the sample (across all seeds) with the highest `sample_ranking_score`, and copies **all files** for that sample into the pair's top-level directory.

```bash
python3 copy_best_rs_of3.py /path/to/openfold3_output_root
```

| Parameter | Description |
|---|---|
| `root_dir` | Root directory containing one subdirectory per protein pair |
| `--dry-run` (optional) | Preview what would be copied without copying anything |

### Option B — Only pull the winning `.cif` model, into one shared directory

[`copy_cifs_of3.py`](./copy_cifs_of3.py) does the same ranking-score comparison, but copies **only the winning `.cif` model file** for each pair into a single, separate output directory.

```bash
python3 copy_cifs_of3.py /path/to/openfold3_output_root /path/to/collected_cifs
```

| Parameter | Description |
|---|---|
| `root_dir` | Root directory containing one subdirectory per protein pair |
| `output_dir` | Directory where the winning `.cif` files will be collected |
| `--dry-run` (optional) | Preview what would be copied without copying anything |
