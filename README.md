# babs-demo-ohbm2025
A demo for OHBM 2025 educational course on BABS

## Overview

This repository demonstrates how to use BIDS App Bootstrap (BABS) with a simple BIDS App that counts volumes in T1-weighted MRI images.

## The BIDS App: T1 Volume Counter

A simple BIDS App that:
- Finds all T1-weighted images in a BIDS dataset
- Counts the number of volumes in each image
- Outputs results in BIDS derivatives format

### Running Locally

```bash
python volume_counter_bidsapp.py <bids_dir> <output_dir> participant
```

### Docker Usage

#### Building the Docker Image

```bash
docker build -t bidsapp/volume-counter .
```

#### Running the Containerized App

For participant level analysis:
```bash
docker run -it --rm \
    -v /path/to/bids/dataset:/data:ro \
    -v /path/to/output:/output \
    bidsapp/volume-counter \
    /data /output participant
```

For specific participants:
```bash
docker run -it --rm \
    -v /path/to/bids/dataset:/data:ro \
    -v /path/to/output:/output \
    bidsapp/volume-counter \
    /data /output participant \
    --participant-label 01 02 03
```

For group level analysis:
```bash
docker run -it --rm \
    -v /path/to/bids/dataset:/data:ro \
    -v /path/to/output:/output \
    bidsapp/volume-counter \
    /data /output group
```

### Output Format

The app creates BIDS-compliant derivatives with:
- `dataset_description.json` - Metadata about the derivatives
- `sub-*/sub-*_T1w-volumes.tsv` - Volume counts per participant
- `sub-*/sub-*_T1w-volumes.json` - Metadata sidecar
- `participants.tsv` - Summary across all participants
