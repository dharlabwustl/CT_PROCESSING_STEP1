#!/bin/bash
SESSION_ID=${1}
XNAT_USER=${2}
XNAT_PASS=${3}
XNAT_HOST=${4}
TYPE_OF_PROGRAM=${5}
echo ${TYPE_OF_PROGRAM}::TYPE_OF_PROGRAM
if [[ ${TYPE_OF_PROGRAM} == 2 ]] ;
then
    /software/processing_before_segmentation.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST  ##/input /output
fi
if [[ ${TYPE_OF_PROGRAM} == 1 ]] ;
then
    /software/processing_after_segmentation.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi
if [[ ${TYPE_OF_PROGRAM} == 3 ]] ;
then
    /software/download_nifti_file.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi

if [[ ${TYPE_OF_PROGRAM} == 4 ]] ;
then
    /software/processing_after_segmentation_csfmaskonly.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi

if [[ ${TYPE_OF_PROGRAM} == 'PREPROCESSING' ]] ;
then
    /software/processing_before_segmentation_03_15_2023.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'POSTPROCESSING' ]] ;
then
    /software/processing_after_segmentation_03_21_2024.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi

##################

if [[ ${TYPE_OF_PROGRAM} == 'PROJECT_LEVEL_PRE_PROCESSING' ]] ;
then
    /software/project_level_pre_processing.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi
if [[ ${TYPE_OF_PROGRAM} == 'PROJECT_LEVEL_AFTER_PROCESSING' ]] ;
then
    /software/project_level_after_processing.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST ##/input /output
fi