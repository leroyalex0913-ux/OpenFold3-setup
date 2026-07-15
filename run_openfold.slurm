#!/bin/bash --login
#SBATCH --job-name=openfold3
#SBATCH --gpus=a100:1
#SBATCH --output=/mnt/scratch/leroyale/af3/logs/%x_%A_%a.out
#SBATCH --error=/mnt/scratch/leroyale/af3/logs/%x_%A_%a.err
#SBATCH --time=3:59:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G

module purge
module load CUDA/12.9.1
cd /mnt/research/woldring_lab/openfold-3

pixi run -e openfold3-cuda12 run_openfold predict \
    --query-json /mnt/home/leroyale/AF3-HPC/PDB_input_of3_short.json \
    --output-dir /mnt/scratch/leroyale/of3/outputs/real_run \
    --num-model-seeds 5