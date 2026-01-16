
#  fill_redcap_for_selected_scan_arguments=('fill_redcap_for_selected_scan' ${xml_filename} ${csvfile_for_redcap} ) #${subj_listfile})
#  outputfiles_present=$(python3 download_with_session_ID.py "${fill_redcap_for_selected_scan_arguments[@]}")
sessionID=${1}
csvfile_for_redcap=${2}
working_dir='/workinginput'

read PROJECT_ID SUBJECT_ID <<< $(
python3 -c "
from utilities_using_xnat_python import given_sessionid_get_project_n_subjectids
p, s = given_sessionid_get_project_n_subjectids('${sessionID}')
if p is not None and s is not None:
    print(p, s)
"
)
SESSION_LABEL=$(
python3 -c "from utilities_using_xnat_python import get_session_label_from_session_id; \
print(get_session_label_from_session_id('${sessionID}'))"
)
ID_VALUE=$(
python3 -c "from utilities_using_xnat_python import get_id_from_nifti_location_csv; print(get_id_from_nifti_location_csv('${sessionID}'))"
)
csvfile_for_redcap_copy=${working_dir}/scan_selection_copy.csv
CLEAN_CSV=$(
python3 -c "
from download_with_session_ID import sanitize_csv_non_ascii_to_O
out = sanitize_csv_non_ascii_to_O('${csvfile_for_redcap}', '${csvfile_for_redcap_copy}')
if out:
    print(out)
"
)

#echo "$CLEAN_CSV"

#  # detect encoding
#file ${csvfile_for_redcap}
#
## convert to UTF-8
#iconv -f CP1252 -t UTF-8 ${csvfile_for_redcap} > ${csvfile_for_redcap}

  #session_label,project_name, subject_name ,csv_file
    SUCCESS_VALUE_0_FAIL_1=$(
python3 -c "from download_with_session_ID import fill_redcap_for_selected_scan_01142026; print(fill_redcap_for_selected_scan_01142026('${SESSION_LABEL}','${PROJECT_ID}','${SUBJECT_ID}','${csvfile_for_redcap_copy}' ))"
)
#  read ACQ_SITE ACQ_DT SCANNER BODY_PART KVP <<< $(
#python3 -c "
#from utilities_using_xnat_python import get_scan_dicom_metadata_from_first_dicom
#a,b,c,d,e = get_scan_dicom_metadata_from_first_dicom('${sessionID}','${ID_VALUE}')
#if a is not None:
#    print(a,b,c,d,e)
#"
#)


  echo SUCCESS_VALUE_0_FAIL_1::$SUCCESS_VALUE_0_FAIL_1::${SUBJECT_ID}:${PROJECT_ID}::${SESSION_LABEL}::${ID_VALUE} ##::ACQ_SITE::${ACQ_SITE}::ACQ_DT::${ACQ_DT}::SCANNER:${SCANNER}::BODY_PART::${BODY_PART}::KVP::${KVP}