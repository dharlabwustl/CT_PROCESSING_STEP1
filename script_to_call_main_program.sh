#!/bin/bash
SESSION_ID=${1}
XNAT_USER=${2}
XNAT_PASS=${3}
XNAT_HOST=${4}
TYPE_OF_PROGRAM=${5}
echo ${TYPE_OF_PROGRAM}::TYPE_OF_PROGRAM
if [[ ${TYPE_OF_PROGRAM} == 2 ]] ;
then
    /software/processing_before_segmentation.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input /output
fi
if [[ ${TYPE_OF_PROGRAM} == 1 ]] ;
then
    /software/processing_after_segmentation.sh $SESSION_ID $XNAT_USER $XNAT_PASS $XNAT_HOST /input /output
fi
