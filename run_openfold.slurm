#!/bin/bash --login
#SBATCH --job-name=openfold3
#SBATCH --gpus=a100:1
#SBATCH --output=/mnt/scratch/
#SBATCH --error=/mnt/scratch/
#SBATCH --time=3:59:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G

module purge
module load CUDA/12.9.1
cd /mnt/research/woldring_lab/openfold-3

pixi run -e openfold3-cuda12 run_openfold predict \
    --query-json /path/to/json/file
    --output-dir /your/output/directory/
