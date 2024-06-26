#!/bin/bash
export MCR_CACHE_ROOT=/workinginput
cd /software/
rm -r /software/*
git_link=${5}
git clone ${git_link}
y=${git_link%.git}
git_dir=$(basename $y)
#find /software/${git_dir}/* -type f -exec sed -i "s/python/\/root\/anaconda3\/envs\/tf\/bin\/python'/g" {} \;
#find /software/${git_dir}/* -type f -exec sed -i "s/python/\/root\/anaconda3\/envs\/tf\/bin\/python'/g" {} \;
mv ${git_dir}/* /software/
cp -r  /Stroke_CT_Processing /software/
chmod +x /software/Stroke_CT_Processing/*.sh
chmod +x /software/*.sh
for x in  /software/Stroke_CT_Processing/*/* ; do chmod +x $x ; done
for x in  /software/Stroke_CT_Processing/* ; do chmod +x $x ; done
find /software/Stroke_CT_Processing/* -type f -exec sed -i "s/\/Stroke_CT_Processing/\/software\/Stroke_CT_Processing/g" {} \;
find /software/Stroke_CT_Processing/step4_bet.sh  -type f -exec sed -i "s/bet/\/usr\/lib\/fsl\/5.0\/bet/g" {} \;
cat  /software/Stroke_CT_Processing/step4_bet.sh
#/usr/lib/fsl/5.0/
#
#cd /software/
#rm -r /software/*
#git_link=${5}
#git clone ${git_link}
#y=${git_link%.git}
#git_dir=$(basename $y)
#mv ${git_dir}/* /software/
#cp -r  /Stroke_CT_Processing/* /software/
#chmod +x /software/*.sh

SESSION_ID=${1}
XNAT_USER=${2}
XNAT_PASS=${3}
XNAT_HOST=${4}
TYPE_OF_PROGRAM=${6}
export REDCAP_API=${7}
/software/script_to_call_main_program.sh $SESSION_ID $XNAT_USER $XNAT_PASS ${XNAT_HOST} ${TYPE_OF_PROGRAM} ${REDCAP_API}
