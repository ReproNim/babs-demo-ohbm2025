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

## 1. Get on HPC and Git Clone this repo (your fork)

```bash
git clone https://github.com/yourgithubusername/babs-demo-ohbm2025
```

We recommend running this demo on a scratch space rather than your home directory on HPC.  

## 2. Install BABS and dependencies

We recommend using `mamba` or `micromamba` for package management.

```bash
cd babs-demo-ohbm2025

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

If build it from Dockerhub, run:

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
cd babs-demo-ohbm2025 # make sure you're in the root folder
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
        #SBATCH --cpus-per-task=1            # Change it accordingly based on your BIDSApp task
        #SBATCH --mem=4G                     # Change it accordingly based on your BIDSApp task
        #SBATCH --time=00:05:00              # Change it accordingly based on your BIDSApp task
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

Then re-submit the jobs with `babs submit` in `counting_project` folder.

Now let's run `babs status`:
```
No jobs in the queue
No jobs in the queue
Job status:
There are in total of 38 jobs to complete.

38 job(s) have been submitted; 0 job(s) haven't been submitted.

Among submitted jobs,
38 job(s) successfully finished;
All jobs are completed!

All log files are located in folder: /orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project/analysis/logs
```

## 8. After jobs have finished

### 8.1. Use babs merge to merge all results and provenance

We now run `babs merge` in `counting_project`:

```bash
babs merge
```

If it was successful, you'll see this message:
```
`babs merge` was successful!
```

Now you're ready to check the results.

### 8.2. Check results

Clone the output RIA as another folder (e.g., called `counting_project_outputs`) to a location external to the BABS project:

```bash
cd ..   # Now, you should be in folder `babs-demo-ohbm2025`, where `counting_project` locates

datalad clone \
    ria+file://${PWD}/counting_project/output_ria#~data \
    counting_project_outputs
```

You'll see:
```
[INFO   ] Configure additional publication dependency on "output-storage"                                                         
configure-sibling(ok): . (sibling)
install(ok): /orcd/scratch/bcs/001/yibei/babs-demo-ohbm2025/counting_project_outputs (dataset)
action summary:
  configure-sibling (ok: 1)
  install (ok: 1)
```

Let's go into this new folder and see what's inside:

```bash
cd counting_project_outputs
ls
```

You'll see:
```
CHANGELOG.md                             sub-0051466_t1-volume-counter-0-1-0.zip  sub-0051481_t1-volume-counter-0-1-0.zip
code                                     sub-0051467_t1-volume-counter-0-1-0.zip  sub-0051482_t1-volume-counter-0-1-0.zip
containers                               sub-0051468_t1-volume-counter-0-1-0.zip  sub-0051483_t1-volume-counter-0-1-0.zip
inputs                                   sub-0051469_t1-volume-counter-0-1-0.zip  sub-0051484_t1-volume-counter-0-1-0.zip
README.md                                sub-0051470_t1-volume-counter-0-1-0.zip  sub-0051485_t1-volume-counter-0-1-0.zip
sub-0051456_t1-volume-counter-0-1-0.zip  sub-0051471_t1-volume-counter-0-1-0.zip  sub-0051486_t1-volume-counter-0-1-0.zip
sub-0051457_t1-volume-counter-0-1-0.zip  sub-0051472_t1-volume-counter-0-1-0.zip  sub-0051487_t1-volume-counter-0-1-0.zip
sub-0051458_t1-volume-counter-0-1-0.zip  sub-0051473_t1-volume-counter-0-1-0.zip  sub-0051488_t1-volume-counter-0-1-0.zip
sub-0051459_t1-volume-counter-0-1-0.zip  sub-0051474_t1-volume-counter-0-1-0.zip  sub-0051489_t1-volume-counter-0-1-0.zip
sub-0051460_t1-volume-counter-0-1-0.zip  sub-0051475_t1-volume-counter-0-1-0.zip  sub-0051490_t1-volume-counter-0-1-0.zip
sub-0051461_t1-volume-counter-0-1-0.zip  sub-0051476_t1-volume-counter-0-1-0.zip  sub-0051491_t1-volume-counter-0-1-0.zip
sub-0051462_t1-volume-counter-0-1-0.zip  sub-0051477_t1-volume-counter-0-1-0.zip  sub-0051492_t1-volume-counter-0-1-0.zip
sub-0051463_t1-volume-counter-0-1-0.zip  sub-0051478_t1-volume-counter-0-1-0.zip  sub-0051493_t1-volume-counter-0-1-0.zip
sub-0051464_t1-volume-counter-0-1-0.zip  sub-0051479_t1-volume-counter-0-1-0.zip
sub-0051465_t1-volume-counter-0-1-0.zip  sub-0051480_t1-volume-counter-0-1-0.zip
```

Let's use `datalad get` and then `unzip -l` to fetch the results:

```bash
datalad get sub-0051456_t1-volume-counter-0-1-0.zip 
unzip -l sub-0051456_t1-volume-counter-0-1-0.zip 
```

You will see the following message:
```
get(ok): sub-0051456_t1-volume-counter-0-1-0.zip (file) [from output-storage...]                                                  

Archive:  sub-0051456_t1-volume-counter-0-1-0.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  06-20-2025 12:58   t1-volume-counter/
      300  06-20-2025 12:58   t1-volume-counter/dataset_description.json
       57  06-20-2025 12:58   t1-volume-counter/participants.tsv
        0  06-20-2025 12:58   t1-volume-counter/sub-0051456/
      239  06-20-2025 12:58   t1-volume-counter/sub-0051456/sub-0051456_T1w-volumes.json
       44  06-20-2025 12:58   t1-volume-counter/sub-0051456/sub-0051456_T1w-volumes.tsv
---------                     -------
      640                     6 files
```

Voilà! Your first BABS project has succeeded! 
