#!/usr/bin/env python3
"""
Simple BIDS App: T1 Volume Counter
This BIDS app counts the number of volumes in T1-weighted images
and outputs the results in BIDS derivatives format.
"""

import os
import sys
import json
import argparse
import nibabel as nib
from pathlib import Path
import logging

__version__ = '0.1.0'

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_dataset_description(output_dir, version):
    """Create dataset_description.json for derivatives"""
    description = {
        "Name": "T1 Volume Counter - BIDS App",
        "BIDSVersion": "1.6.0",
        "DatasetType": "derivative",
        "GeneratedBy": [{
            "Name": "T1 Volume Counter",
            "Version": version,
            "CodeURL": "https://github.com/ReproNim/babs-demo-ohbm2025"
        }]
    }
    
    # Create main app output directory
    app_dir = output_dir / 't1-volume-counter'
    app_dir.mkdir(exist_ok=True, parents=True)
    
    desc_file = app_dir / 'dataset_description.json'
    with open(desc_file, 'w') as f:
        json.dump(description, f, indent=4)

def find_t1w_images(bids_dir):
    """Find all T1w images in BIDS dataset"""
    t1w_files = []
    
    # Walk through subject directories
    for subject_dir in bids_dir.glob('sub-*'):
        if not subject_dir.is_dir():
            continue
            
        # Check for sessions
        session_dirs = list(subject_dir.glob('ses-*'))
        if session_dirs:
            # Multi-session dataset
            for session_dir in session_dirs:
                anat_dir = session_dir / 'anat'
                if anat_dir.exists():
                    t1w_files.extend(anat_dir.glob('*_T1w.nii.gz'))
                    t1w_files.extend(anat_dir.glob('*_T1w.nii'))
        else:
            # Single-session dataset
            anat_dir = subject_dir / 'anat'
            if anat_dir.exists():
                t1w_files.extend(anat_dir.glob('*_T1w.nii.gz'))
                t1w_files.extend(anat_dir.glob('*_T1w.nii'))
    
    return sorted(t1w_files)

def count_volumes(nifti_file):
    """Count number of volumes in a NIfTI file"""
    try:
        img = nib.load(nifti_file)
        shape = img.shape
        
        # For 3D images (typical T1w), number of volumes is 1
        if len(shape) == 3:
            return 1
        # For 4D images, the 4th dimension is number of volumes
        elif len(shape) == 4:
            return shape[3]
        else:
            return None
    except Exception as e:
        logging.error(f"Error loading {nifti_file}: {e}")
        return None

def parse_filename(filepath):
    """Parse BIDS filename to extract entities"""
    filename = filepath.stem.replace('.nii', '')
    parts = filename.split('_')
    
    entities = {}
    for part in parts[:-1]:  # Last part is suffix (e.g., T1w)
        if '-' in part:
            key, value = part.split('-', 1)
            entities[key] = value
    
    return entities

def process_dataset(bids_dir, output_dir, participant_label=None):
    """Process BIDS dataset and count volumes"""
    logger = logging.getLogger(__name__)
    
    # Find all T1w images
    t1w_files = find_t1w_images(bids_dir)
    logger.info(f"Found {len(t1w_files)} T1w images")
    
    # Filter by participant if specified
    if participant_label:
        # Remove 'sub-' prefix if it exists
        clean_label = participant_label.replace('sub-', '')
        t1w_files = [f for f in t1w_files if f'sub-{clean_label}' in str(f)]
        logger.info(f"Processing {len(t1w_files)} T1w images for participant sub-{clean_label}")
    
    results = []
    
    for t1w_file in t1w_files:
        logger.debug(f"Processing {t1w_file}")
        
        # Count volumes
        n_volumes = count_volumes(t1w_file)
        
        if n_volumes is not None:
            # Parse filename for metadata
            entities = parse_filename(t1w_file)
            
            # Create result entry
            result = {
                'subject': entities.get('sub', 'unknown'),
                'session': entities.get('ses', None),
                'run': entities.get('run', None),
                'filename': t1w_file.name,
                'n_volumes': n_volumes
            }
            
            # Remove None values
            result = {k: v for k, v in result.items() if v is not None}
            
            results.append(result)
            logger.info(f"{t1w_file.name}: {n_volumes} volumes")
    
    return results

def save_results(results, output_dir):
    """Save results in BIDS derivatives format"""
    # Create main app output directory for 7z compatibility
    app_dir = output_dir / 't1-volume-counter'
    app_dir.mkdir(exist_ok=True, parents=True)
    
    # Group results by subject
    subjects = {}
    for result in results:
        sub = result['subject']
        if sub not in subjects:
            subjects[sub] = []
        subjects[sub].append(result)
    
    # Save per-subject TSV files
    for sub, sub_results in subjects.items():
        # Create subject directory
        sub_dir = app_dir / f'sub-{sub}'
        sub_dir.mkdir(exist_ok=True, parents=True)
        
        # Prepare TSV data
        tsv_file = sub_dir / f'sub-{sub}_T1w-volumes.tsv'
        json_file = sub_dir / f'sub-{sub}_T1w-volumes.json'
        
        # Write TSV
        with open(tsv_file, 'w') as f:
            # Header
            if any('session' in r for r in sub_results):
                f.write('filename\tsession\tn_volumes\n')
                for r in sub_results:
                    session = r.get('session', 'n/a')
                    f.write(f"{r['filename']}\t{session}\t{r['n_volumes']}\n")
            else:
                f.write('filename\tn_volumes\n')
                for r in sub_results:
                    f.write(f"{r['filename']}\t{r['n_volumes']}\n")
        
        # Write JSON sidecar
        sidecar = {
            'Description': 'Number of volumes in T1-weighted images',
            'Sources': [r['filename'] for r in sub_results],
            'n_volumes': {
                'Description': 'Number of 3D volumes in the NIfTI file',
                'Units': 'volumes'
            }
        }
        
        with open(json_file, 'w') as f:
            json.dump(sidecar, f, indent=4)
    
    # Save group-level summary
    summary_file = app_dir / 'participants.tsv'
    with open(summary_file, 'w') as f:
        f.write('participant_id\tn_t1w_scans\ttotal_volumes\n')
        for sub, sub_results in subjects.items():
            n_scans = len(sub_results)
            total_volumes = sum(r['n_volumes'] for r in sub_results)
            f.write(f"sub-{sub}\t{n_scans}\t{total_volumes}\n")

def main():
    parser = argparse.ArgumentParser(
        description='BIDS App: T1 Volume Counter - Counts volumes in T1w images',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('bids_dir', type=Path,
                        help='The directory with the input dataset '
                             'formatted according to the BIDS standard.')
    parser.add_argument('output_dir', type=Path,
                        help='The directory where the output files '
                             'should be stored.')
    parser.add_argument('analysis_level', choices=['participant', 'group'],
                        help='Level of the analysis that will be performed. '
                             'Multiple participant level analyses can be run '
                             'independently (in parallel) using the same '
                             'output_dir.')
    parser.add_argument('--participant-label', '--participant_label',
                        help='The label(s) of the participant(s) that should be analyzed. '
                             'The label corresponds to sub-<participant_label> from the BIDS spec '
                             '(so it does not include "sub-"). If this parameter is not '
                             'provided all subjects should be analyzed. Multiple '
                             'participants can be specified with a space separated list.',
                        nargs="+")
    parser.add_argument('-v', '--version', action='version',
                        version=f'BIDS App: T1 Volume Counter version {__version__}')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Validate inputs
    if not args.bids_dir.exists():
        logger.error(f"Input BIDS directory does not exist: {args.bids_dir}")
        sys.exit(1)
    
    # Create output directory
    args.output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create dataset description
    create_dataset_description(args.output_dir, __version__)
    
    # Process based on analysis level
    if args.analysis_level == "participant":
        if args.participant_label:
            # Process specific participants
            for label in args.participant_label:
                # Remove 'sub-' prefix if present in label
                clean_label = label.replace('sub-', '')
                logger.info(f"Processing participant: sub-{clean_label}")
                results = process_dataset(args.bids_dir, args.output_dir, clean_label)
                if results:
                    save_results(results, args.output_dir)
        else:
            # Process all participants
            logger.info("Processing all participants")
            results = process_dataset(args.bids_dir, args.output_dir)
            if results:
                save_results(results, args.output_dir)
    
    elif args.analysis_level == "group":
        # For this simple app, group level just ensures summary exists
        logger.info("Group level analysis - ensuring summary files exist")
        app_dir = args.output_dir / 't1-volume-counter'
        summary_file = app_dir / 'participants.tsv'
        if not summary_file.exists():
            logger.warning("No participant-level results found. Run participant level first.")
    
    logger.info("Processing complete!")

if __name__ == '__main__':
    main()
