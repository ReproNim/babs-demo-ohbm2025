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

We have already created a YAML configuration file (`babs_config.yaml`) for the T1 Volume Counter BIDS App. This file tells BABS how to run your containerized app on the HPC cluster.

### Key sections you may need to modify:

**Input Dataset:**
```yaml
input_datasets:
    BIDS:
        origin_url: "/orcd/data/satra/002/datasets/simple2_datalad/abide1/Caltech"
```
- Change `origin_url` to point to your DataLad BIDS dataset
- This example uses ABIDE-I data from Caltech site

**Cluster Resources:**
```yaml
cluster_resources:
    customized_text: |
        #SBATCH --partition=mit_preemptable  # Change to your partition
        #SBATCH --cpus-per-task=1
        #SBATCH --mem=8G
        #SBATCH --time=00:05:00
```
- Update `--partition` to match your HPC cluster's partition names
- Adjust memory and time limits based on your needs

**Compute Space:**
```yaml
job_compute_space: "/orcd/scratch/bcs/001/yibei/t1_volume_counter_compute"
```
- Change this path to your scratch/compute directory on the HPC

**Environment Setup:**
```yaml
script_preamble: |
    source ~/.bashrc 
    micromamba activate babs
    module load apptainer/1.1.9
```
- Modify the module load command if your HPC uses different module names
- Update the conda/mamba environment activation if needed

For more detailed information on configuring YAML files for BABS, see the [BABS documentation](https://pennlinc-babs.readthedocs.io/en/stable/walkthrough.html#step-1-3-prepare-a-yaml-file-for-the-bids-app).

## 6. Create a BABS project

Run the following command to initialize your BABS project:

```bash
babs init \
    --container_ds ${PWD}/bidsapp-container \
    --container_name t1-volume-counter-0-1-0 \
    --container_config ${PWD}/babs_config.yaml \
    --processing_level subject \
    --queue slurm \
    /orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project
```

**Expected output:**
```
BABS project has been initialized! Path to this BABS project: '/orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project'
`babs init` was successful!
```

This command:
- Uses the containerized BIDS App we prepared earlier
- Configures it with our YAML file
- Sets up subject-level processing
- Configures for SLURM job scheduler
- Creates the project in your scratch directory

**Note:** `/orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project` is the BABS project folder that will be created automatically through `babs init`. Update this path to match your scratch directory.

After `babs init`, navigate to your BABS project folder and verify the setup:

```bash
cd counting_project
babs check-setup
```

**Expected output:**
```
`babs check-setup` was successful!
```

## 7. Job submission and job status

Navigate to your BABS project folder (`counting_project` in this case) and submit jobs:

```bash
cd counting_project
babs submit
```

In our case, we see:
```
Submitting the following jobs:
         sub_id  submitted  has_results  is_failed    job_id  task_id state time_used time_limit  nodes  cpus partition name
0   sub-0051456      False        False      False  66936634        1   nan       nan        nan      0     0       nan  nan
1   sub-0051457      False        False      False  66936634        2   nan       nan        nan      0     0       nan  nan
...
37  sub-0051493      False        False      False  66936634       38   nan       nan        nan      0     0       nan  nan
```

Check job status:
```bash
babs status
```

In our case, all jobs failed:
```
No jobs in the queue
No jobs in the queue
Job status:
There are in total of 38 jobs to complete.

38 job(s) have been submitted; 0 job(s) haven't been submitted.

Among submitted jobs,
0 job(s) successfully finished;
0 job(s) are pending;
0 job(s) are running;
38 job(s) failed.

All log files are located in folder: /orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project/analysis/logs
```

### Troubleshooting failed jobs

Check the log files:
```bash
ls /orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project/analysis/logs
```

Look at an error log:
```bash
cat /orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project/analysis/logs/t1-.e66936634_1
```

The error shows:
```
/var/spool/slurmd/job66936637/slurm_script: line 27: cd: /orcd/scratch/bcs/001/yibei/t1_volume_counter_compute: No such file or directory
```

**Fix:** Create the missing compute directory:
```bash
mkdir -p /orcd/scratch/bcs/001/yibei/t1_volume_counter_compute
```

Then re-submit the jobs with `babs submit`.

### Output Format

The app creates BIDS-compliant derivatives with:
- `dataset_description.json` - Metadata about the derivatives
- `sub-*/sub-*_T1w-volumes.tsv` - Volume counts per participant
- `sub-*/sub-*_T1w-volumes.json` - Metadata sidecar
- `participants.tsv` - Summary across all participants
