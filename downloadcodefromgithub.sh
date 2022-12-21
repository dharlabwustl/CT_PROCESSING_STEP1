#!/bin/bash
cd /software/
rm -r /software/*
git_link=${5}
git clone ${git_link}
y=${git_link%.git}
git_dir=$(basename $y)
mv ${git_dir}/* /software/
cp -r  /Stroke_CT_Processing/* /software/
chmod +x /software/*.sh 

SESSION_ID=${1}
XNAT_USER=${2}
XNAT_PASS=${3}
XNAT_HOST=${4}
TYPE_OF_PROGRAM=${6}

/software/script_to_call_main_program.sh $SESSION_ID $XNAT_USER $XNAT_PASS ${XNAT_HOST} ${TYPE_OF_PROGRAM}
