#!/bin/bash
#
# local_segmentation_pipeline.sh
#
# Run the CT preprocessing + segmentation pipeline on a LOCAL NIfTI file.
# All XNAT download/upload logic removed.
#
# Usage:
#   ./local_segmentation_pipeline.sh /path/to/input.nii.gz \
#       [/workinginput] [/workingoutput] [/outputinsidedocker]
#
# Defaults (if not provided):
#   working_dir         = /workinginput
#   output_directory    = /workingoutput
#   final_output_dir    = /outputinsidedocker
#

set -euo pipefail

# ------------- Arguments ------------------------------------------------------

#if [[ $# -lt 1 ]]; then
#  echo "Usage: $0 /path/to/input.nii.gz [/workinginput] [/workingoutput] [/outputinsidedocker]"
#  exit 1
#fi

INPUT_NIFTI=$(ls /input/SCANS/2/NIFTI/*.nii) ##$1"
working_dir="${2:-/workinginput}"
output_directory="${3:-/workingoutput}"
final_output_directory="${4:-/outputinsidedocker}"

#if [[ ! -f "$INPUT_NIFTI" ]]; then
#  echo "ERROR: Input NIfTI file not found: $INPUT_NIFTI"
#  exit 1
#fi

echo ">>> Input NIfTI            : $INPUT_NIFTI"
echo ">>> Working directory      : $working_dir"
echo ">>> Output directory       : $output_directory"
echo ">>> Final output directory : $final_output_directory"

# ------------- Prepare directories -------------------------------------------

mkdir -p "$working_dir" "$output_directory" "$final_output_directory"

# Optional: clean old contents (comment out if you don't want auto-clean)
rm -f "${working_dir}"/* || true
rm -f "${output_directory}"/* || true
rm -f "${final_output_directory}"/* || true

# Copy local NIfTI into working_dir
echo ">>> Copying input NIfTI to working directory..."
cp "$INPUT_NIFTI" "$working_dir/"

# ------------- Run your existing processing steps ----------------------------

echo ">>> Running stroke_ct_processing_1.sh ..."
#/software/Stroke_CT_Processing/stroke_ct_processing_1.sh \
#  "$working_dir" "$output_directory"
#
#echo ">>> Running step4_bet.sh ..."
#/software/Stroke_CT_Processing/step4_bet.sh \
#  "$output_directory"
#
#echo ">>> Running stroke_ct_processing_2.sh ..."
#/software/Stroke_CT_Processing/stroke_ct_processing_2.sh \
#  "$output_directory" "$output_directory"
/software/Stroke_CT_Processing/stroke_ct_processing_3.sh ${working_dir} ${output_directory}
# ------------- Collect results locally ---------------------------------------

echo ">>> Copying results to final output directory..."
cp "${output_directory}"/* "${final_output_directory}/" || true

echo ">>> Segmentation pipeline finished."
echo ">>> Final results are in: ${final_output_directory}"
