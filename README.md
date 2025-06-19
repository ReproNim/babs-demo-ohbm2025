# babs-demo-ohbm2025
A demo for OHBM 2025 educational course on BABS

## Overview

This repository demonstrates how to use BIDS App Bootstrap (BABS) with a simple BIDS App that counts volumes in T1-weighted MRI images.

## What do we need

- This repository - make a fork of this repo
- BABS environment (including DataLad, git-annex)
- HPC (SLURM or SGE, we will use SLURM in this demo)
- A BIDS App
- A BIDS dataset (we will use ABIDE-I in this demo)

## 1. Get on HPC and Git Clone this repo

```bash
git clone https://github.com/yourgithubusername/babs-demo-ohbm2025
cd babs-demo-ohbm2025
```

## 2. Install BABS and dependencies

```bash
# Install into a new environment called babs:
mamba create -f environment_hpc.yml

# Activate the environment:
mamba activate babs
```

For more details, see the [BABS installation documentation](https://pennlinc-babs.readthedocs.io/en/stable/installation.html).

## 3. Prepare input BIDS dataset(s) as DataLad dataset(s)

Here we use an existing DataLad BIDS dataset on our cluster. For more details on how to prepare BIDS dataset(s) as DataLad dataset(s), see the [BABS documentation](https://pennlinc-babs.readthedocs.io/en/stable/preparation_input_dataset.html#id3).

## 4. Prepare containerized BIDS App as a DataLad dataset

Here we use a BIDS App that counts T1 volume. We have it on Docker Hub and also in this repo.

You can build a Singularity file from Docker Hub using either Apptainer or Singularity depending on what your HPC supports.

If you build it from Docker, run:

```bash
# Load module first if needed
module load apptainer/1.1.9

# Build the image
apptainer build \
    t1-volume-counter-0.1.0.sif \
    docker://yibeichen/t1-volume-counter:0.1.0
```

Or use the SIF from this repo directly:

```bash
cd babs-demo-ohbm2025
echo "Current directory: $PWD"

datalad create -D "demo BIDS App" bidsapp-container
cd bidsapp-container
datalad containers-add \
    --url ${PWD}/../t1-volume-counter-0.1.0.sif \
    t1-volume-counter-0-1-0
```

## 5. Prepare a YAML file for this t1-volume-counter app

## 6. Create a BABS project

### Output Format

The app creates BIDS-compliant derivatives with:
- `dataset_description.json` - Metadata about the derivatives
- `sub-*/sub-*_T1w-volumes.tsv` - Volume counts per participant
- `sub-*/sub-*_T1w-volumes.json` - Metadata sidecar
- `participants.tsv` - Summary across all participants
