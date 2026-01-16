#!/usr/bin/python
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os, sys, errno, shutil, uuid,subprocess,csv,json
import math,inspect
import glob
import re,time,xnat
import requests
import pandas as pd
import nibabel as nib
import numpy as np
# import pydicom as dicom
import pathlib
import argparse,xmltodict
from xnatSession import XnatSession
import inspect
# import xnat
from datetime import datetime
import traceback
import utilities_using_xnat_python # given_sessionid_get_project_n_subjectids
# from biomarker_db_module import BiomarkerDB
from biomarkerdbclass import  BiomarkerDB
from redcapapi_functions import *
catalogXmlRegex = re.compile(r'.*\.xml$')
XNAT_HOST_URL=os.environ['XNAT_HOST']  #'http://snipr02.nrg.wustl.edu:8080' #'https://snipr02.nrg.wustl.edu' #'https://snipr.wustl.edu'
XNAT_HOST = XNAT_HOST_URL # os.environ['XNAT_HOST'] #
XNAT_USER = os.environ['XNAT_USER']#
XNAT_PASS =os.environ['XNAT_PASS'] #
api_token=os.environ['REDCAP_API']
xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
xnatSession.renew_httpsession()
class arguments:
    def __init__(self,stuff=[]):
        self.stuff=stuff

#
# def get_project_subject_session_from_session_id(session_id):
#     """
#     Given an XNAT session (experiment) ID, return:
#       - project_name
#       - subject_name (subject label)
#       - session_label
#
#     Returns:
#       (project_name, subject_name, session_label) OR (None, None, None) on failure
#     """
#     func_name = inspect.currentframe().f_code.co_name
#
#     try:
#         with xnat.connect(XNAT_HOST, user=XNAT_USER, password=XNAT_PASS) as conn:
#             if session_id not in conn.experiments:
#                 return None, None, None
#
#             exp = conn.experiments[session_id]
#
#             project_name = exp.project
#             subject_name = exp.subject.label
#             session_label = exp.label
#
#             return project_name, subject_name, session_label
#
#     except Exception:
#         ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         err = (
#             f"[{ts}] Function: {func_name}\n"
#             f"Session ID: {session_id}\n"
#             f"Traceback:\n{traceback.format_exc()}\n"
#             f"{'-'*80}\n"
#         )
#         with open(LOG_FILE, "a") as f:
#             f.write(err)
#
#         return None, None, None
#

def call_fill_google_mysql_db_with_single_value(args):
    db_table_name=args.stuff[1]
    session_id=args.stuff[2]
    column_name=args.stuff[3]
    column_value=args.stuff[4]
    try:
        fill_google_mysql_db_with_single_value(db_table_name, session_id,column_name,column_value)
    except:
        pass

def call_fill_google_mysql_db_from_csv(args):
    db_table_name=args.stuff[1]
    csv_file_path=args.stuff[2]
    id_column=args.stuff[3]
    # column_value=args.stuff[4]
    try:
        fill_google_mysql_db_from_csv(db_table_name, csv_file_path, id_column=id_column)
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
        subprocess.call(command,shell=True)
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
        subprocess.call(command,shell=True)
        pass

def fill_google_mysql_db_from_csv(db_table_name, csv_file_path, id_column="session_id"):
      # Replace with actual module path
    command = f"echo  I am at : {db_table_name}::{csv_file_path}::{id_column}::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
    subprocess.call(command,shell=True)
    try:
        df = pd.read_csv(csv_file_path)
        command = f"echo  I am at 1 : {db_table_name}::{csv_file_path}::{id_column}::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
        subprocess.call(command,shell=True)
    except Exception as e:
        # print(f"Failed to load CSV: {e}")
        command = f"echo  failed at : {e}::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
        subprocess.call(command,shell=True)
        return
    db = BiomarkerDB(
        host=os.environ["GOOGLE_MYSQL_DB_IP"],
        user="root",
        password=os.environ["GOOGLE_MYSQL_DB_PASS"],
        database="BIOMARKERS"
    )


    if not db.initialized:
        print("Database initialization failed.")
        command = f"echo  failed at : Database initialization failed.::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
        subprocess.call(command,shell=True)
        return
    command = f"echo  I am  at : {id_column}::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
    subprocess.call(command,shell=True)
    for index, row in df.iterrows():
        session_id = row[id_column]

        for column_name in df.columns:
            if column_name == id_column:
                continue  # Skip ID column
            column_value = row[column_name]
            try:
                db.upsert_single_field_by_id(db_table_name, session_id, column_name, column_value)
                command = f"echo  I am  at : {id_column}::{session_id}::{db_table_name}::{session_id}::{column_name}::{column_value}::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
                subprocess.call(command,shell=True)
            except Exception as e:
                print(f"Failed to insert {column_name}={column_value} for session_id={session_id}: {e}")
                command = f"echo  failed at : {column_name}::{column_value}::{e}::" +  inspect.stack()[0][3]  + " >> " + "/output/error1.txt"
                subprocess.call(command,shell=True)

    db.close()


def fill_google_mysql_db_with_single_value(db_table_name, session_id,column_name,column_value):
    db = BiomarkerDB(
        host=os.environ["GOOGLE_MYSQL_DB_IP"],             # Replace with your instance IP
        user="root",                     # Replace if using a different user
        password=os.environ["GOOGLE_MYSQL_DB_PASS"] , ##"dharlabwustl1!",   # Replace with your actual password
        database="BIOMARKERS"
    )
    try:
        if db.initialized:
            db.upsert_single_field_by_id(db_table_name, session_id, column_name, column_value)
            db.close()
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        pass

def pipeline_step_completed(db_table_name,session_id,scan_id,column_name,column_value,resource_dir,list_of_file_ext_tobe_checked):
    try:
        # list_of_file_ext_tobe_checked_len=len(list_of_file_ext_tobe_checked)
        count=0
        URI=f'/data/experiments/{session_id}/scans/{scan_id}'
        list_of_files_in_resource_dir=get_resourcefiles_metadata(URI,resource_dir)
        df_scan_resource = pd.read_json(json.dumps(list_of_files_in_resource_dir)) #pd.read_json(json.dumps(metadata_masks))
        # Check if each extension exists in **any** row in the url column
        ext_found = [any(df_scan_resource['URI'].str.contains(ext, case=False)) for ext in list_of_file_ext_tobe_checked]

        # Final decision: are all extensions found at least once in any row?
        all_found = int(all(ext_found))
        if all_found==1:
            column_value=1 #all_found
        # pd.DataFrame(df_scan).to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
        fill_google_mysql_db_with_single_value(db_table_name, session_id,column_name,column_value)
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        pass
    return 1
def call_pipeline_step_completed(args):
    db_table_name=args.stuff[1]
    session_id=args.stuff[2]
    scan_id=args.stuff[3]
    column_name=args.stuff[4]
    column_value=args.stuff[5]
    resource_dir=args.stuff[6]
    list_of_file_ext_tobe_checked=args.stuff[7:]
    try:
        pipeline_step_completed(db_table_name,session_id,scan_id,column_name,column_value,resource_dir,list_of_file_ext_tobe_checked)
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        pass
    return 1

def get_scan_id_given_session_id_N_niftiname(session_id,niftiname):
    this_session_metadata=get_metadata_session(session_id)
    this_session_metadata_df = pd.read_json(json.dumps(this_session_metadata))
    this_scan_id=''
    for session_each_metadata_id, session_each_metadata in this_session_metadata_df.iterrows():
        URL='/data/experiments/'+session_id+'/scans/'+str(session_each_metadata['ID'])
        metadata_nifti=get_resourcefiles_metadata(URL,'NIFTI')
        df_scan = pd.read_json(json.dumps(metadata_nifti))
        for df_scan_each_id, df_scan_each in df_scan.iterrows():
            if niftiname in str(df_scan_each['Name']): #.split('.ni')[0]==niftiname:
                this_scan_id=str(session_each_metadata['ID'])
    return this_scan_id
def get_scan_quality(session_id,scan_id,scan_assessor_name):
    try:
        url = ("/data/experiments/%s/scans/%s/assessors?format=json" %    (session_id,scan_id))
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        response = xnatSession.httpsess.get(xnatSession.host + url)
        #xnatSession.close_httpsession())
        print(get_field_from_nested_dict(response.json(), scan_assessor_name))
        return get_field_from_nested_dict(response.json(), scan_assessor_name)
    except Exception as e:
        print(e)
    return None
def get_field_from_nested_dict(data, target_field):
    try:
        if isinstance(data, dict):
            # Check if the target field is in the dictionary
            if target_field in data:
                return data[target_field]
            # Recursively search in the dictionary
            for key, value in data.items():
                result = get_field_from_nested_dict(value, target_field)
                if result is not None:
                    return result
        elif isinstance(data, list):
            # Iterate through the list and search in each element
            for item in data:
                result = get_field_from_nested_dict(item, target_field)
                if result is not None:
                    return result
    except Exception as e:
        print(e)
        pass
    return None
def change_type_of_scan(sessionId, scanId,label):
    returnvalue=0
    try:

        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        url = ("/data/experiments/%s/scans/%s?xsiType=xnat:ctScanData&type=%s" % (sessionId, scanId, label))
        #xnatSession.renew_httpsession()
        response = xnatSession.httpsess.put(xnatSession.host + url)
        url = ("/data/experiments/%s/scans/%s?xsiType=xnat:ctScanData&quality=%s" % (sessionId, scanId, 'usable'))
        #xnatSession.renew_httpsession()
        response1 = xnatSession.httpsess.put(xnatSession.host + url)
        if response.status_code == 200 or response1.status_code == 200:
            print("Successfully set type for %s scan %s to '%s'" % (sessionId, scanId, label))
            print("Successfully set usability for %s scan %s to '%s'" % (sessionId, scanId, 'usable'))
            command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
            subprocess.call(command,shell=True)
            returnvalue=1
        # else:
        #     errStr = "ERROR"
        #     if response.status_code == 403 or response.status_code == 404:
        #         errStr = "PERMISSION DENIED"
        #     raise Exception("%s attempting to set series_class for %s %s to '%s': %s" %
        #                     (errStr, sessionId, scanId, label, response.text))
    except Exception:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        pass
    return  returnvalue


def call_change_type_of_scan(args):
    returnvalue=0
    try:
        sessionId=args.stuff[1]
        scanId=args.stuff[2]
        label=args.stuff[3]
        change_type_of_scan(sessionId, scanId,label)
    except Exception:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        pass
    return  returnvalue
def merge_csvs(csvfileslist,columntomatchlist,outputfilename):
    df1=pd.read_csv(csvfileslist[0])
    left_on=columntomatchlist[0]
    for x in range(len(csvfileslist)):
        if x > 0:
            df2=pd.read_csv(csvfileslist[x])
            df_cd = pd.merge(df1, df2, how='inner', left_on = 'Id', right_on = 'Id')

            df2.rename(columns={csvfileslist[x]:left_on}, inplace=True)
            df1 = df1.merge(df2, left_on = left_on, right_on = columntomatchlist[x])
            left_on=columntomatchlist[x]

def combinecsvs_general(inputdirectory,outputdirectory,outputfilename,extension):
    outputfilepath=os.path.join(outputdirectory,outputfilename)
    extension = 'csv'
    # pdffilesuffix='.csv'
    # pdffiledirectory=inputdirectory
    # all_filenames = get_latest_filesequence(pdffilesuffix,pdffiledirectory)
    all_filenames = [i for i in glob.glob(os.path.join(inputdirectory,'*{}'.format(extension)))]
#    os.chdir(inputdirectory)
    #combine all files in the list
    combined_csv=pd.read_csv(all_filenames[0])

    for x in all_filenames:
        try:
            x_df=pd.read_csv(x)

            # print(x_df.shape)
            combined_csv=pd.concat([combined_csv,pd.read_csv(x)])
        except:
            pass

    # combined_csv = pd.concat([pd.read_csv(all_filenames[0]),pd.read_csv(all_filenames[0])],axis=0) ##[pd.read_csv(f) for f in all_filenames ],axis=0)
    combined_csv = combined_csv.drop_duplicates()
    # combined_csv['FileName_slice'].replace('', np.nan, inplace=True)
    # combined_csv.dropna(subset=['FileName_slice'], inplace=True)
    #export to csv
    combined_csv.to_csv(outputfilepath, index=False, encoding='utf-8-sig')
    # combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    # combined_csv = combined_csv.drop_duplicates()
    # combined_csv['FileName_slice'].replace('', np.nan, inplace=True)
    # combined_csv.dropna(subset=['FileName_slice'], inplace=True)
    # #export to csv
    # combined_csv.to_csv(outputfilepath, index=False, encoding='utf-8-sig')
def combinecsvs(inputdirectory,outputdirectory,outputfilename,extension):
    outputfilepath=os.path.join(outputdirectory,outputfilename)
    extension = 'csv'
    pdffilesuffix='.csv'
    pdffiledirectory=inputdirectory
    all_filenames = get_latest_filesequence(pdffilesuffix,pdffiledirectory)

    # print([f for f in all_filenames ])
    # all_filenames = [i for i in glob.glob(os.path.join(inputdirectory,'*{}'.format(extension)))]
    # print(all_filenames)
    #    os.chdir(inputdirectory)
    #combine all files in the list
    combined_csv=pd.read_csv(all_filenames[0])

    for x in all_filenames:
        try:
            x_df=pd.read_csv(x)

            # print(x_df.shape)
            combined_csv=pd.concat([combined_csv,pd.read_csv(x)])
        except:
            pass

    # combined_csv = pd.concat([pd.read_csv(all_filenames[0]),pd.read_csv(all_filenames[0])],axis=0) ##[pd.read_csv(f) for f in all_filenames ],axis=0)
    combined_csv = combined_csv.drop_duplicates()
    combined_csv['FileName_slice'].replace('', np.nan, inplace=True)
    combined_csv.dropna(subset=['FileName_slice'], inplace=True)
    #export to csv
    combined_csv.to_csv(outputfilepath, index=False, encoding='utf-8-sig')
def combinecsvs_inafileoflist(listofcsvfiles_filename,outputdirectory,outputfilename):
    try:
        listofcsvfiles_filename_df=pd.read_csv(listofcsvfiles_filename)
        listofcsvfiles_filename_df_list=list(listofcsvfiles_filename_df['LOCAL_FILENAME'])
        outputfilepath=os.path.join(outputdirectory,outputfilename)
        all_filenames = [i for i in listofcsvfiles_filename_df_list]
        combined_csv=pd.read_csv(all_filenames[0])
        for x in all_filenames:
            try:
                combined_csv=pd.concat([combined_csv,pd.read_csv(x)])
            except:
                pass
        combined_csv = combined_csv.drop_duplicates()
        combined_csv.to_csv(outputfilepath, index=False, encoding='utf-8-sig')

        print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
        return 0
def call_combinecsvs_inafileoflist(args):
    try:
        listofcsvfiles_filename=args.stuff[1]
        outputdirectory=args.stuff[2]
        outputfilename=args.stuff[3]
        combinecsvs_inafileoflist(listofcsvfiles_filename,outputdirectory,outputfilename)
        print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
        return 0
def combinecsvs_withprefix(inputdirectory,outputdirectory,outputfilename,prefix):
    outputfilepath=os.path.join(outputdirectory,outputfilename)
    extension = 'csv'
    all_filenames = [i for i in glob.glob(os.path.join(inputdirectory,'{}*.{}'.format(prefix,extension)))]
    #    os.chdir(inputdirectory)
    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    combined_csv = combined_csv.drop_duplicates()
    #export to csv
    combined_csv.to_csv(outputfilepath, index=False, encoding='utf-8-sig')

def copy_latest_pdffile(pdffileprefix,pdffiledirectory,destinationdirectory):
    pdffilesuffix='.pdf'
    allfileswithprefix1=get_latest_filesequence(pdffilesuffix,pdffiledirectory) #glob.glob(os.path.join(pdffiledirectory,pdffileprefix+'*'))
    if len(allfileswithprefix1)>0:
        # allfileswithprefix=sorted(allfileswithprefix1, key=os.path.getmtime)
        # filetocopy=allfileswithprefix[0]
        for filetocopy in allfileswithprefix1:
            command = 'cp ' + filetocopy +'  ' + destinationdirectory
            subprocess.call(command,shell=True)
def get_latest_filesequence(pdffilesuffix,pdffiledirectory):
    latest_file_list=[]
    allfileswithprefix1=glob.glob(os.path.join(pdffiledirectory,'*'+pdffilesuffix))
    allfileswithprefix1_df = pd.DataFrame(allfileswithprefix1)
    allfileswithprefix1_df.columns=["FILENAME"]
    # print(allfileswithprefix1_df)
    allfileswithprefix1_df=allfileswithprefix1_df[allfileswithprefix1_df.FILENAME.str.contains("_thresh")]
    allfileswithprefix1_df['DATE']=allfileswithprefix1_df['FILENAME']
    allfileswithprefix1_df['PREFIX']=allfileswithprefix1_df['FILENAME']
    # allfileswithprefix1_df[['FILENAME', 'EXT']] = allfileswithprefix1_df['FILENAME'].str.split('.pdf', 1, expand=True) _thres
    allfileswithprefix1_df[['PREFIX', 'EXT']] = allfileswithprefix1_df['PREFIX'].str.split('_thresh', 1, expand=True)
    allfileswithprefix1_df['DATE'] = allfileswithprefix1_df['DATE'].str[-14:-4]
    allfileswithprefix1_df['DATE'] = allfileswithprefix1_df['DATE'].str.replace('_', '')
    allfileswithprefix1_df["PREFIX"]=allfileswithprefix1_df["PREFIX"].apply(lambda x: os.path.splitext(os.path.basename(x))[0])
    # print(allfileswithprefix1_df['PREFIX']) #[0])
    # print(np.unique(allfileswithprefix1_df['PREFIX']).shape)
    # print(allfileswithprefix1_df['PREFIX'].shape)
    unique_session_name=np.unique(allfileswithprefix1_df['PREFIX'])
    allfileswithprefix1_df['DATETIME'] =    allfileswithprefix1_df['DATE']
    allfileswithprefix1_df['DATETIME'] = pd.to_datetime(allfileswithprefix1_df['DATETIME'], format='%m%d%Y', errors='coerce')
    # print(allfileswithprefix1_df['DATETIME'])
    # print(unique_session_name)
    for x in range(unique_session_name.shape[0]):
        # print(unique_session_name[x])
        x_df=allfileswithprefix1_df.loc[allfileswithprefix1_df['PREFIX'] == unique_session_name[x]]
        x_df = x_df.sort_values(by=['DATETIME'], ascending=False)
        x_df=x_df.reset_index(drop=True)
        # print(x_df)
        # if len(allfileswithprefix1)>0:
        #     allfileswithprefix=sorted(allfileswithprefix1, key=os.path.getmtime)
        filetocopy=x_df['FILENAME'][0]
        # print(len(x_df['DATE'][0]))
        # if len(x_df['DATE'][0])==8:
        latest_file_list.append(filetocopy)
    #     # command = 'cp ' + filetocopy +'  ' + destinationdirectory
    #     # subprocess.call(command,shell=True)
    return latest_file_list
def call_copy_latest_csvfile():
    pdffileprefix=sys.argv[1]
    pdffiledirectory=sys.argv[2]
    destinationdirectory=sys.argv[3]
    try:
        copy_latest_pdffile(pdffileprefix,pdffiledirectory,destinationdirectory)
    except:
        pass
def copy_latest_csvfile(pdffileprefix,pdffiledirectory,destinationdirectory):
    allfileswithprefix1=glob.glob(os.path.join(pdffiledirectory,pdffileprefix+'*'))
    if len(allfileswithprefix1)>0:
        allfileswithprefix=sorted(allfileswithprefix1, key=os.path.getmtime)
        filetocopy=allfileswithprefix[0]
        command = 'cp ' + filetocopy +'  ' + destinationdirectory
        subprocess.call(command,shell=True)
def call_copy_latest_pdffile():
    pdffileprefix=sys.argv[1]
    pdffiledirectory=sys.argv[2]
    destinationdirectory=sys.argv[3]
    try:
        copy_latest_pdffile(pdffileprefix,pdffiledirectory,destinationdirectory)
    except:
        pass

def call_combine_all_csvfiles_of_edema_biomarker():
    working_directory=sys.argv[1]
    working_directory_tocombinecsv=sys.argv[2]
    extension=sys.argv[3]
    outputfilename=sys.argv[4]
    combinecsvs(working_directory,working_directory_tocombinecsv,outputfilename,extension)
def call_combine_all_csvfiles_general():
    working_directory=sys.argv[1]
    working_directory_tocombinecsv=sys.argv[2]
    extension=sys.argv[3]
    outputfilename=sys.argv[4]
    combinecsvs_general(working_directory,working_directory_tocombinecsv,outputfilename,extension)
def call_combine_all_csvfiles_of_edema_biomarker_withprefix():
    working_directory=sys.argv[1]
    working_directory_tocombinecsv=sys.argv[2]
    prefix=sys.argv[3]
    outputfilename=sys.argv[4]
    combinecsvs_withprefix(working_directory,working_directory_tocombinecsv,outputfilename,prefix)
def call_get_all_selected_scan_in_a_project():
    projectId=sys.argv[1]
    working_directory=sys.argv[2]
    get_all_selected_scan_in_a_project(projectId,working_directory)


def call_get_all_EDEMA_BIOMARKER_csvfiles_of_allselectedscan():
    working_directory=sys.argv[1]
    get_all_EDEMA_BIOMARKER_csvfiles_of_ascan(working_directory)


def call_get_all_BIOMARKER_csvfiles_of_allselectedscan():
    working_directory=sys.argv[1]
    resource_dir=sys.argv[2]
    # get_all_EDEMA_BIOMARKER_csvfiles_of_ascan(working_directory)
    get_all_BIOMARKER_csvfiles_of_ascan(working_directory,resource_dir)
def add_a_column(csvfile,columname,columnvalue):
    aa = pd.read_csv(csvfile)
    aa[columname] = columnvalue
    aa.to_csv(csvfile,index=False)
def call_add_a_column():
    csvfile=sys.argv[1]
    columname=sys.argv[2]
    columnvalue=sys.argv[3]
    add_a_column(csvfile,columname,columnvalue)

def merge_files_with_col_name(file1,file2,colname1,colname2):
    csvfile=sys.argv[1]
    columname=sys.argv[2]
    columnvalue=sys.argv[3]
    add_a_column(csvfile,columname,columnvalue)


def get_all_EDEMA_BIOMARKER_csvfiles_of_ascan(dir_to_receive_the_data):
    for each_csvfile in glob.glob(os.path.join(dir_to_receive_the_data,'SNIPR*.csv')):
        try:
            df_selected_scan=pd.read_csv(each_csvfile)
            resource_dir='EDEMA_BIOMARKER'
            # print(df_selected_scan)
            for item_id1, each_selected_scan in df_selected_scan.iterrows():
                scan_URI=each_selected_scan['URI'].split('/resources/')[0] #/data/experiments/SNIPR_E03516/scans/2/resources/110269/files/BJH_002_11112019_1930_2.nii
                print(scan_URI)
                metadata_EDEMA_BIOMARKERS=get_resourcefiles_metadata(scan_URI,resource_dir)
                if len(metadata_EDEMA_BIOMARKERS) >0:
                    metadata_EDEMA_BIOMARKERS_df=pd.DataFrame(metadata_EDEMA_BIOMARKERS)
                    print(metadata_EDEMA_BIOMARKERS_df)
                    for item_id, each_file_inEDEMA_BIOMARKERS in metadata_EDEMA_BIOMARKERS_df.iterrows():
                        if '.csv' in each_file_inEDEMA_BIOMARKERS['URI']:
                            print("YES IT IS CSV FILE FOR ANALYSIS")
                            downloadresourcefilewithuri_py(each_file_inEDEMA_BIOMARKERS,dir_to_receive_the_data)
                        if '.pdf' in each_file_inEDEMA_BIOMARKERS['URI']:
                            print("YES IT IS PDF FILE FOR VISUALIZATION")
                            downloadresourcefilewithuri_py(each_file_inEDEMA_BIOMARKERS,dir_to_receive_the_data)
                            # break
                    # break
        except:
            pass


def get_all_BIOMARKER_csvfiles_of_ascan(dir_to_receive_the_data,resource_dir):
    for each_csvfile in glob.glob(os.path.join(dir_to_receive_the_data,'SNIPR*.csv')):
        try:
            df_selected_scan=pd.read_csv(each_csvfile)
            # resource_dir='EDEMA_BIOMARKER'
            # print(df_selected_scan)
            for item_id1, each_selected_scan in df_selected_scan.iterrows():
                scan_URI=each_selected_scan['URI'].split('/resources/')[0] #/data/experiments/SNIPR_E03516/scans/2/resources/110269/files/BJH_002_11112019_1930_2.nii
                print(scan_URI)
                metadata_EDEMA_BIOMARKERS=get_resourcefiles_metadata(scan_URI,resource_dir)
                if len(metadata_EDEMA_BIOMARKERS) >0:
                    metadata_EDEMA_BIOMARKERS_df=pd.DataFrame(metadata_EDEMA_BIOMARKERS)
                    print(metadata_EDEMA_BIOMARKERS_df)
                    for item_id, each_file_inEDEMA_BIOMARKERS in metadata_EDEMA_BIOMARKERS_df.iterrows():
                        if '.csv' in each_file_inEDEMA_BIOMARKERS['URI']:
                            print("YES IT IS CSV FILE FOR ANALYSIS")
                            downloadresourcefilewithuri_py(each_file_inEDEMA_BIOMARKERS,dir_to_receive_the_data)
                        if '.pdf' in each_file_inEDEMA_BIOMARKERS['URI']:
                            print("YES IT IS PDF FILE FOR VISUALIZATION")
                            downloadresourcefilewithuri_py(each_file_inEDEMA_BIOMARKERS,dir_to_receive_the_data)
                            # break
                    # break
        except:
            pass



# def combine_all_csvfiles_of_edema_biomarker(projectId,dir_to_receive_the_data):

#     ## for each csv file corresponding to the session
#     for each_csvfile in glob.glob(os.path.join(dir_to_receive_the_data,'*.csv')):
#         df_selected_scan=pd.read_csv(each_csvfile)
#         resource_dir='EDEMA_BIOMARKER'
#         for item_id1, each_selected_scan in df_selected_scan.iterrows():
#             scan_URI=each_selected_scan['URI'].split('/resources/')[0] #/data/experiments/SNIPR_E03516/scans/2/resources/110269/files/BJH_002_11112019_1930_2.nii
#             metadata_EDEMA_BIOMARKERS=get_resourcefiles_metadata(scan_URI,resource_dir)
#             metadata_EDEMA_BIOMARKERS_df=pd.DataFrame(metadata_EDEMA_BIOMARKERS)
#             for item_id, each_file_inEDEMA_BIOMARKERS in sessions_list_df.iterrows():
#                 # print(each_file_inEDEMA_BIOMARKERS['URI'])
#                 if '.csv' in each_file_inEDEMA_BIOMARKERS['URI']:
#                     print("YES IT IS CSV FILE FOR ANALYSIS")
#                     downloadresourcefilewithuri_py(each_file_inEDEMA_BIOMARKERS,dir_to_receive_the_data)
#                 if '.pdf' in each_file_inEDEMA_BIOMARKERS['URI']:
#                     print("YES IT IS CSV FILE FOR ANALYSIS")
#                     downloadresourcefilewithuri_py(each_file_inEDEMA_BIOMARKERS,dir_to_receive_the_data)


#     # get_resourcefiles_metadata(URI,resource_dir)
#     ## download csv files from the EDEMA_BIOMARKER directory:


#     ## combine all the csv files

#     ## upload the combined csv files to the project directory level


def deleteafile(filename):
    command="rm " + filename
    subprocess.call(command,shell=True)
def get_all_selected_scan_in_a_project(projectId,dir_to_receive_the_data):
    sessions_list=get_allsessionlist_in_a_project(projectId)
    sessions_list_df=pd.DataFrame(sessions_list)
    for item_id, each_session in sessions_list_df.iterrows():
        sessionId=each_session['ID']
        output_csvfile=os.path.join(dir_to_receive_the_data,sessionId+'.csv')
        try:
            decision_which_nifti(sessionId,dir_to_receive_the_data,output_csvfile)
        except:
            pass

def get_allsessionlist_in_a_project(projectId):
    # projectId="BJH" #sys.argv[1]
    url = ("/data/projects/%s/experiments/?format=json" %    (projectId))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    sessions_list=response.json()['ResultSet']['Result']

    return sessions_list
def call_decision_which_nifti():
    sessionId=sys.argv[1]
    dir_to_receive_the_data=sys.argv[2]
    output_csvfile=sys.argv[3]
    decision_which_nifti(sessionId,dir_to_receive_the_data,output_csvfile)

def call_decision_which_nifti_multiplescans():
    sessionId=sys.argv[1]
    dir_to_receive_the_data=sys.argv[2]
    output_csvfile=sys.argv[3]
    decision_which_nifti_multiplescans(sessionId,dir_to_receive_the_data,output_csvfile)
def count_brainaxial_or_thin(sessionId):
    numberof_thin_or_axialscans=[0,0]
    try:

        this_session_metadata=get_metadata_session(sessionId)
        jsonStr = json.dumps(this_session_metadata)
        # print(jsonStr)
        df = pd.read_json(jsonStr)
        try :
            numberof_thin_or_axialscans[0]=numberof_thin_or_axialscans[0]+df['type'].value_counts()['Z-Axial-Brain']
        except:
            pass
        try :
            numberof_thin_or_axialscans[1]=numberof_thin_or_axialscans[1]+df['type'].value_counts()['Z-Brain-Thin']
        except:
            pass
        # numberof_thin_or_axialscans=[df['type'].value_counts()['Z-Axial-Brain'] , df['type'].value_counts()['Z-Brain-Thin']]
        return  numberof_thin_or_axialscans #str(df_1.iloc[0][metadata_field])
    except Exception:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        print("Exception::{}".format(Exception))
        pass
    return numberof_thin_or_axialscans
def count_niftifiles_insession(sessionId,dir_to_receive_the_data):
    numberofniftifiles=[0,""]
    try:

        this_session_metadata=get_metadata_session(sessionId)
        jsonStr = json.dumps(this_session_metadata)
        # print(jsonStr)
        df = pd.read_json(jsonStr)
        for item_id, each_axial in df.iterrows():
            URI=each_axial['URI'] #args.stuff[1] #sys.argv[1]
            resource_dir="NIFTI" #args.stuff[2] #sys.argv[2]
            output_csvfile=os.path.join(dir_to_receive_the_data,sessionId+URI.split("/")[-1]+".csv") #args.stuff[4] #sys.argv[4]
            get_resourcefiles_metadata_saveascsv(URI,resource_dir,dir_to_receive_the_data,output_csvfile)

            try :
                output_csvfile_df=pd.read_csv(output_csvfile)
                for item_id1, each_axial1 in output_csvfile_df.iterrows():
                    if ".nii" in each_axial1['Name']:
                        numberofniftifiles[0]=numberofniftifiles[0]+1
                        numberofniftifiles[1]="_".join(each_axial1['Name'].split("_")[0:len(each_axial1['Name'].split("_"))-1])

            except:
                pass
            print("I PASSED AT ::{}".format(inspect.stack()[0][3]))

        #
        # numberofniftifiles=df['type'].value_counts()['Z-Axial-Brain'] + df['type'].value_counts()['Z-Brain-Thin']
        # print("numberofniftifiles::{}".format(numberofniftifiles))
        return  numberofniftifiles #str(df_1.iloc[0][metadata_field])
    except Exception:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        print("Exception::{}".format(Exception))
        pass
    return numberofniftifiles
def get_single_value_from_metadata_forascan(sessionId,scanId,metadata_field):
    returnvalue=""
    try:

        this_session_metadata=get_metadata_session(sessionId)
        jsonStr = json.dumps(this_session_metadata)
        # print(jsonStr)
        df = pd.read_json(jsonStr)
        df['ID']=df['ID'].apply(str)
        # this_session_metadata_df_scanid=df1[df1['ID'] == str(scanId1)]
        df_1=df.loc[(df['ID'] == str(scanId))]
        df_1=df_1.reset_index()
        print(" I AM AT get_single_value_from_metadata_forascan")
        print(df.columns)
        print("I SUCCEEDED AT ::{}".format(inspect.stack()[0][3]))
        return str(df_1.iloc[0][metadata_field])
    except Exception:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        print("Exception::{}".format(Exception))
        pass
    return returnvalue
def decision_which_nifti_multiplescans(sessionId,dir_to_receive_the_data="",output_csvfile=""):
    this_session_metadata=get_metadata_session(sessionId)
    jsonStr = json.dumps(this_session_metadata)
    # print(jsonStr)
    df = pd.read_json(jsonStr)

    # # df = pd.read_csv(sessionId+'_scans.csv')
    # sorted_df = df.sort_values(by=['type'], ascending=False)
    # # sorted_df.to_csv('scan_sorted.csv', index=False)
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] != 'unusable')] # | (df['type'] == 'Z-Brain-Thin')  & (df['quality'] == 'usable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin')  & (df['quality'] != 'unusable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    # print(df_axial)
    list_of_usables=[]
    list_of_usables_withsize=[]
    file_uploaded_flag=0
    if len(df_axial)>0:
        selectedFile=""
    # print(len(df_axial))
    # print("df_axial:{}".format(len(df_axial['URI'])))
        for item_id, each_axial in df_axial.iterrows():
            print(each_axial['URI'])
            URI=each_axial['URI']
            resource_dir='NIFTI'
            nifti_metadata=json.dumps(get_resourcefiles_metadata(URI,resource_dir)) #get_niftifiles_metadata(each_axial['URI'] )) get_resourcefiles_metadata(URI,resource_dir)
            df_scan = pd.read_json(nifti_metadata)

            for each_item_id,each_nifti in df_scan.iterrows():
                print(each_nifti['URI'])
                if '.nii' in each_nifti['Name'] or '.nii.gz' in each_nifti['Name']:
                    # list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID']])
                    x=[each_nifti['URI'],each_nifti['Name'],each_axial['ID']]
                    print("X::{}".format(x))
                    # # pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
                    # # now=time.localtime()
                    # # date_time = time.strftime("_%m_%d_%Y",now)
                    niftifile_location=os.path.join(dir_to_receive_the_data,each_nifti['Name'].split(".nii")[0]+"_NIFTILOCATION.csv")

                    downloadniftiwithuri(x,dir_to_receive_the_data)
                    number_slice=nifti_number_slice(os.path.join(dir_to_receive_the_data,x[1]))
                    # final_ct_file=[[each_nifti['URI'],each_nifti['Name'],each_axial['ID'],number_slice]]
                    list_of_usables_withsize=[]
                    if number_slice >=20 and number_slice <=100:
                        list_of_usables_withsize.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID'],number_slice])
                        jsonStr = json.dumps(list_of_usables_withsize)
                        # print(jsonStr)
                        df = pd.read_json(jsonStr)
                        df.columns=['URI','Name','ID','NUMBEROFSLICES']
                        df.to_csv(niftifile_location,index=False)
                        resource_dirname="NIFTI_LOCATION"
                        url = (("/data/experiments/%s") % (sessionId))
                        uploadsinglefile_with_URI(url,niftifile_location,resource_dirname)
                        file_uploaded_flag=1
    if len(df_thin)>0 and file_uploaded_flag==0:
        selectedFile=""
        # print(len(df_axial))
        # print("df_axial:{}".format(len(df_axial['URI'])))
        df_axial=df_thin

        for item_id, each_axial in df_axial.iterrows():
            print(each_axial['URI'])
            URI=each_axial['URI']
            resource_dir='NIFTI'
            nifti_metadata=json.dumps(get_resourcefiles_metadata(URI,resource_dir)) #get_niftifiles_metadata(each_axial['URI'] )) get_resourcefiles_metadata(URI,resource_dir)
            df_scan = pd.read_json(nifti_metadata)

            for each_item_id,each_nifti in df_scan.iterrows():
                print(each_nifti['URI'])
                if '.nii' in each_nifti['Name'] or '.nii.gz' in each_nifti['Name']:
                    # list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID']])
                    x=[each_nifti['URI'],each_nifti['Name'],each_axial['ID']]
                    print("X::{}".format(x))
                    # # pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
                    # # now=time.localtime()
                    # # date_time = time.strftime("_%m_%d_%Y",now)
                    niftifile_location=os.path.join(dir_to_receive_the_data,each_nifti['Name'].split(".nii")[0]+"_NIFTILOCATION.csv")

                    downloadniftiwithuri(x,dir_to_receive_the_data)
                    number_slice=nifti_number_slice(os.path.join(dir_to_receive_the_data,x[1]))
                    # final_ct_file=[[each_nifti['URI'],each_nifti['Name'],each_axial['ID'],number_slice]]
                    list_of_usables_withsize=[]
                    if number_slice <=200:
                        list_of_usables_withsize.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID'],number_slice])
                        jsonStr = json.dumps(list_of_usables_withsize)
                        # print(jsonStr)
                        df = pd.read_json(jsonStr)
                        df.columns=['URI','Name','ID','NUMBEROFSLICES']
                        df.to_csv(niftifile_location,index=False)
                        resource_dirname="NIFTI_LOCATION"
                        url = (("/data/experiments/%s") % (sessionId))
                        uploadsinglefile_with_URI(url,niftifile_location,resource_dirname)

        return
def get_info_from_xml(xmlfile):
    try:
        # session_id=args.stuff[1]
        # xmlfile=args.stuff[2]
        subprocess.call("echo " + "I xmlfile AT ::{}  >> /workingoutput/error.txt".format(xmlfile) ,shell=True )
        with open(xmlfile, encoding="utf-8") as fd:
            xmlfile_dict = xmltodict.parse(fd.read())

        project_name=''
        subject_name=''
        session_label=''
        acquisition_site_xml=''
        acquisition_datetime_xml=''
        scanner_from_xml=''
        body_part_xml=''
        kvp_xml=''
        try:
            session_label=xmlfile_dict['xnat:CTSession']['@label']
        except:
            pass
        try:
            project_name=xmlfile_dict['xnat:CTSession']['@project']
        except:
            pass
        try:
            subject_name=str(xmlfile_dict['xnat:CTSession']['xnat:dcmPatientName'])
        except:
            pass
        # Acquisition site
        try:
            acquisition_site_xml=xmlfile_dict['xnat:CTSession']['xnat:acquisition_site']
        except:
            pass
        try:
            date_split=str(xmlfile_dict['xnat:CTSession']['xnat:date']).split('-')
            columnvalue_1="/".join([date_split[1],date_split[2],date_split[0]])
            columnvalue_2=":".join(str(xmlfile_dict['xnat:CTSession']['xnat:time']).split(':')[0:2])
            acquisition_datetime_xml=columnvalue_1+" "+ columnvalue_2
        except:
            pass
        columnvalue_1=""
        columnvalue_2=""
        try:
            for xx in range(len(xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'])):
                if xx > 1:
                    try:
                        columnvalue_1= xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'][xx]['xnat:scanner']['@manufacturer']
                        if len(columnvalue_1)>1:
                            break
                    except:
                        pass
            for xx in range(len(xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'])):
                if xx > 1:
                    try:
                        columnvalue_2=  xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'][xx]['xnat:scanner']['@model']
                        if len(columnvalue_2)>1:
                            break
                    except:
                        pass

            scanner_from_xml= columnvalue_1 + " " + columnvalue_2
        except:
            pass
        ################
        try:
            for xx in range(len(xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'])):
                if xx>1:
                    try:
                        body_part_xml=xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'][xx]['xnat:bodyPartExamined']
                        # fill_datapoint_each_sessionn_1(identifier,columnname,columnvalue,csvfilename)
                        if len(body_part_xml)>3:
                            break
                    except:
                        pass

        except:
            pass
        ###############
        ###############

        try:
            for xx in range(len(xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'])):
                if xx>1:
                    try:
                        kvp_xml=xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'][xx]['xnat:parameters']['xnat:kvp']
                        # fill_datapoint_each_sessionn_1(identifier,columnname,columnvalue,csvfilename)
                        if len(kvp_xml)>1:
                            break
                    except:
                        pass
            # columnvalue=xmlfile_dict['xnat:CTSession']['xnat:scans']['xnat:scan'][0]['xnat:parameters']['xnat:kvp']
            # fill_datapoint_each_sessionn_1(identifier,columnname,columnvalue,csvfilename)
        except:
            subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
            pass
        ###############

        subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        subprocess.call("echo " + "I PASSED AT project_name::{}  >> /workingoutput/error.txt".format(project_name) ,shell=True )
        subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
        subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label) ,shell=True )
        subprocess.call("echo " + "I PASSED AT acquisition_site_xml::{}  >> /workingoutput/error.txt".format(acquisition_site_xml) ,shell=True )
        subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        subprocess.call("echo " + "I PASSED AT acquisition_datetime_xml::{}  >> /workingoutput/error.txt".format(acquisition_datetime_xml) ,shell=True )
        subprocess.call("echo " + "I PASSED AT scanner_from_xml::{}  >> /workingoutput/error.txt".format(scanner_from_xml) ,shell=True )
        subprocess.call("echo " + "I PASSED AT body_part_xml::{}  >> /workingoutput/error.txt".format(body_part_xml) ,shell=True )
        subprocess.call("echo " + "I PASSED AT kvp_xml::{}  >> /workingoutput/error.txt".format(kvp_xml) ,shell=True )
    except:
        # print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass
    return   project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml
def fill_single_val_redcap(args):
    xmlfile=args.stuff[1]
    csvfilename=args.stuff[2]
    project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml=get_info_from_xml(xmlfile)
    this_project_redcapfile_latest=project_name+'_latest.csv'
    # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
    df_scan_latest=download_latest_redcapfile(api_token,this_project_redcapfile_latest)
    this_session_redcap_repeat_instance_df=df_scan_latest[df_scan_latest['snipr_session']==session_label]
    this_session_redcap_repeat_instance=str(this_session_redcap_repeat_instance_df['redcap_repeat_instance'])
    add_one_data_to_redcap(subject_name,'imaging_data',this_session_redcap_repeat_instance,each_colname,csv_file_df[each_colname])
    return

def find_num_axial_thin(args):
    sessionId=args.stuff[1]
    csvfilename=args.stuff[2]
    this_session_metadata=get_metadata_session(sessionId)
    jsonStr = json.dumps(this_session_metadata)
    # print(jsonStr)
    df = pd.read_json(jsonStr)
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] != 'unusable')] ##| (df['type'] == 'Z-Brain-Thin')]
    df_axial_num=0
    if df_axial.shape[0]>0:
        df_axial_num=df_axial.shape[0]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin')  & (df['quality'] != 'unusable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    df_axial_thin_num=0
    if df_thin.shape[0]>0:
        df_axial_thin_num=df_thin.shape[0]
    list_values_df=pd.DataFrame([df_axial_num,df_axial_thin_num])
    list_values_df=list_values_df.T
    list_values_df.columns=['axial_number','axial_thin_number']
    list_values_df.to_csv(csvfilename,index=False)
    return

def select_scan_for_analysis(args):
    sessionId=args.stuff[1]
    csvfilename=args.stuff[2]
    dir_to_receive_the_data=args.stuff[3]
    this_session_metadata=get_metadata_session(sessionId)
    jsonStr = json.dumps(this_session_metadata)
    # print(jsonStr)
    df = pd.read_json(jsonStr)
    df['NUMBEROFSLICES']=0
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] != 'unusable')] ##| (df['type'] == 'Z-Brain-Thin')]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin')  & (df['quality'] != 'unusable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    try:
        df_axial=df_axial.reset_index()
        for each_id in range(df_axial.shape[0]):
            subprocess.call("echo " + "I PASSED AT each_id::{}  >> /workingoutput/error.txt".format(each_id) ,shell=True )
            URI=df_axial.at[each_id,'URI']
            resource_dir='DICOM'
            scan_meta_data=get_resourcefiles_metadata(URI,resource_dir)
            jsonStr_scan = json.dumps(scan_meta_data)
            # print(jsonStr)
            df_scan = pd.read_json(jsonStr_scan)
            df_axial.at[each_id,'NUMBEROFSLICES']=df_scan.shape[0]
    except:
        pass
    df_scan.to_csv('test_df_scan.csv')
    try:

        df_thin=df_thin.reset_index()
        for each_id in range(df_thin.shape[0]):
            subprocess.call("echo " + "I PASSED AT each_id::{}  >> /workingoutput/error.txt".format(each_id) ,shell=True )
            URI=df_thin.at[each_id,'URI']
            resource_dir='DICOM'
            scan_meta_data=get_resourcefiles_metadata(URI,resource_dir)
            jsonStr_scan = json.dumps(scan_meta_data)
            # print(jsonStr)
            df_scan = pd.read_json(jsonStr_scan)
            df_thin.at[each_id,'NUMBEROFSLICES']=df_scan.shape[0]
    except:
        pass

    if df_axial.shape[0]>0:
        df_maxes = df_axial[df_axial['NUMBEROFSLICES']==df_axial['NUMBEROFSLICES'].max()]
    elif df_thin.shape[0]>0:
        df_maxes = df_thin[df_thin['NUMBEROFSLICES']==df_thin['NUMBEROFSLICES'].max()]
######################
    # return df_maxes

    final_ct_file=''
    if df_maxes.shape[0]>0:
        final_ct_file=df_maxes.iloc[:1]
        for item_id, each_scan in df_maxes.iterrows():

            if "tilt" in each_scan['Name']:
                final_ct_file=each_scan
                break
    if final_ct_file.shape[0] >= 1:
        final_ct_file_df= final_ct_file #pd.DataFrame(final_ct_file)
        for row_id, row_item in final_ct_file.iterrows():
            niftifile_location=os.path.join(dir_to_receive_the_data,row_item['Name'].split(".nii")[0]+"_NIFTILOCATION.csv")
            final_ct_file_df.to_csv(niftifile_location,index=False)
            resource_dirname="NIFTI_LOCATION"
            url = (("/data/experiments/%s") % (sessionId))
            uploadsinglefile_with_URI(url,niftifile_location,resource_dirname)

#############################
    df.to_csv(csvfilename,index=False)
    return
def fill_redcap_for_selected_scan(args):

    try:

        # session_id=args.stuff[1]
        # subprocess.call("echo " + "I zai zeli AT ::{}  >> /workingoutput/error.txt".format(session_id) ,shell=True )
        xmlfile=args.stuff[1]
        # csv_file_df=pd.read_csv(args.stuff[2])
        sanitize_csv_non_ascii_to_O(args.stuff[2], args.stuff[2].split('.csv')[0]+'_copy.csv')
        csv_file_df = pd.read_csv(args.stuff[2].split('.csv')[0]+'_copy.csv')
        subprocess.call("echo " + "I PASSED AT xmlfile::{}  >> /workingoutput/error.txt".format(xmlfile), shell=True)
        # project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml
        project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml=get_info_from_xml(xmlfile)
        this_project_redcapfile_latest=project_name+'_latest.csv'
        subprocess.call("echo " + "I PASSED AT subject_name::subject_name::{}  >> /workingoutput/error.txt".format(subject_name),
                        shell=True)
        subprocess.call(
            "echo " + "I PASSED AT xmlfile::{}  >> /workingoutput/error.txt".format('fill_redcap_for_selected_scan'),
            shell=True)
        # return
        # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
        api_token = os.environ['REDCAP_API']
        df_scan_latest=download_latest_redcapfile(api_token,this_project_redcapfile_latest)
        this_session_redcap_repeat_instance_df=df_scan_latest[df_scan_latest['snipr_session']==session_label]
        this_session_redcap_repeat_instance=str(this_session_redcap_repeat_instance_df['redcap_repeat_instance'].item())
        imaging_data_complete=str(this_session_redcap_repeat_instance_df['imaging_data_complete'].item())
        if imaging_data_complete != '2':
            for each_colname in csv_file_df.columns:
                # print(each_colname)
                # print(csv_file_df[each_colname])
                subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
                subprocess.call("echo " + "I PASSED AT this_session_redcap_repeat_instance::{}  >> /workingoutput/error.txt".format(this_session_redcap_repeat_instance) ,shell=True )
                subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label) ,shell=True )
                subprocess.call("echo " + "I PASSED AT each_colname::{}  >> /workingoutput/error.txt".format(each_colname) ,shell=True )
                subprocess.call("echo " + "I PASSED AT each_colname_value::{}  >> /workingoutput/error.txt".format(csv_file_df[each_colname][0]) ,shell=True )
                try:
                    add_one_data_to_redcap(subject_name,'imaging_data',this_session_redcap_repeat_instance,str(each_colname),csv_file_df[each_colname].item())
                except:
                    subprocess.call("echo " + "I FAILED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
                    pass
        #fill scan base
        ## fill scan complete name
        ## fill number of slices,kvp,px,pz, scanner detail

        # subprocess.call("echo " + "I PASSED AT project_name::{}  >> /workingoutput/error.txt".format(project_name) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT acquisition_site_xml::{}  >> /workingoutput/error.txt".format(acquisition_site_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT acquisition_datetime_xml::{}  >> /workingoutput/error.txt".format(acquisition_datetime_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT scanner_from_xml::{}  >> /workingoutput/error.txt".format(scanner_from_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT body_part_xml::{}  >> /workingoutput/error.txt".format(body_part_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT kvp_xml::{}  >> /workingoutput/error.txt".format(kvp_xml) ,shell=True )
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass
    return
#
import unicodedata

import re

def replace_non_ascii_with_O(s):
    if not s:
        return s
    return "".join(c if ord(c) < 128 else "O" for c in str(s))

import os
import inspect
import re
import subprocess


def remove_non_ascii(inputfile, outputfile):
    with open(inputfile) as f:
        new_text = re.sub(r'[^\x00-\x7F]+', '', f.read())

    with open(outputfile, 'w') as f:
        f.write(new_text)
def sanitize_csv_non_ascii_to_O(
    input_csv: str,
    output_csv: str = None,
    overwrite: bool = False,
):
    """
    Replace any non-ASCII character in an entire CSV file with 'O'.

    Bash usage:
      out = sanitize_csv_non_ascii_to_O(path, overwrite=True)
      if out: print(out)

    Returns:
      - Path to written CSV on success
      - None on failure
    """
    try:
        if not input_csv or not os.path.exists(input_csv):
            subprocess.call(
                "echo 'I FAILED AT csvfile::{} (file not found)' >> /workingoutput/error.txt".format(
                    input_csv
                ),
                shell=True,
            )
            return None

        # Decide output path
        if overwrite:
            out_path = input_csv
        else:
            out_path = output_csv or (input_csv + ".ascii.csv")

        pattern = re.compile(r"[^\x00-\x7F]")

        # Line-by-line processing (safe for large files)
        with open(input_csv, "r", encoding="utf-8", errors="replace") as fin, \
             open(out_path, "w", encoding="utf-8", newline="") as fout:

            for line in fin:
                fout.write(pattern.sub("O", line))

        # PASS log
        subprocess.call(
            "echo 'I PASSED AT csvfile::{}' >> /workingoutput/error.txt".format(
                out_path
            ),
            shell=True,
        )

        return out_path

    except Exception as e:
        subprocess.call(
            "echo 'I FAILED AT csvfile::{} (exception)' >> /workingoutput/error.txt".format(
                input_csv
            ),
            shell=True,
        )
        return None

def clean_ascii(s):
    if not s:
        return s
    s = unicodedata.normalize("NFKD", s)
    return s.encode("ascii", "ignore").decode("ascii")
def fill_redcap_for_selected_scan_01142026(session_label,project_name, subject_name ,csv_file):
    try:

        # session_id=args.stuff[1]
        # subprocess.call("echo " + "I zai zeli AT ::{}  >> /workingoutput/error.txt".format(session_id) ,shell=True )
        # xmlfile=args.stuff[1]

        csv_file_df=pd.read_csv(csv_file) ###args.stuff[2])
        # subprocess.call("echo " + "I PASSED AT xmlfile::{}  >> /workingoutput/error.txt".format(xmlfile),shell=True)
        # return
        # project_name,subject_name, session_label=given_sessionid_get_project_n_subjectids(session_id)
        # project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml
        # project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml=get_info_from_xml(xmlfile)
        # project_name, subject_name = utilities_using_xnat_python.given_sessionid_get_project_n_subjectids(session_id)
        # session_label=session_id
        subprocess.call("echo " + "I PASSED AT project_name::{}  >> /workingoutput/error.txt".format(project_name),
                        shell=True)
        subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name),
                        shell=True)
        subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label),
                        shell=True)
        # return
        subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name),
                        shell=True)
        this_project_redcapfile_latest=project_name+'_latest.csv'
        # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
        api_token = os.environ['REDCAP_API']
        df_scan_latest=download_latest_redcapfile(api_token,this_project_redcapfile_latest)
        this_session_redcap_repeat_instance_df=df_scan_latest[df_scan_latest['snipr_session']==session_label]
        this_session_redcap_repeat_instance=str(this_session_redcap_repeat_instance_df['redcap_repeat_instance'].item())
        imaging_data_complete=str(this_session_redcap_repeat_instance_df['imaging_data_complete'].item())
        if imaging_data_complete != '2':
            for each_colname in csv_file_df.columns:
                # print(each_colname)
                # print(csv_file_df[each_colname])
                subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
                subprocess.call("echo " + "I PASSED AT this_session_redcap_repeat_instance::{}  >> /workingoutput/error.txt".format(this_session_redcap_repeat_instance) ,shell=True )
                subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label) ,shell=True )
                subprocess.call("echo " + "I PASSED AT each_colname::{}  >> /workingoutput/error.txt".format(each_colname) ,shell=True )
                subprocess.call("echo " + "I PASSED AT each_colname_value::{}  >> /workingoutput/error.txt".format(csv_file_df[each_colname][0]) ,shell=True )
                try:
                    add_one_data_to_redcap(subject_name,'imaging_data',this_session_redcap_repeat_instance,str(each_colname),replace_non_ascii_with_O(csv_file_df[each_colname].item()))
                except:
                    subprocess.call("echo " + "I FAILED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
                    pass
        #fill scan base
        ## fill scan complete name
        ## fill number of slices,kvp,px,pz, scanner detail

        # subprocess.call("echo " + "I PASSED AT project_name::{}  >> /workingoutput/error.txt".format(project_name) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT acquisition_site_xml::{}  >> /workingoutput/error.txt".format(acquisition_site_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT acquisition_datetime_xml::{}  >> /workingoutput/error.txt".format(acquisition_datetime_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT scanner_from_xml::{}  >> /workingoutput/error.txt".format(scanner_from_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT body_part_xml::{}  >> /workingoutput/error.txt".format(body_part_xml) ,shell=True )
        # subprocess.call("echo " + "I PASSED AT kvp_xml::{}  >> /workingoutput/error.txt".format(kvp_xml) ,shell=True )
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass
    return
#
#

def fill_redcap_for_pdffile(args):
    try:

        # session_id=args.stuff[1]
        # subprocess.call("echo " + "I zai zeli AT ::{}  >> /workingoutput/error.txt".format(session_id) ,shell=True )
        xmlfile=args.stuff[1]
        file_name=args.stuff[2]
        project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml=get_info_from_xml(xmlfile)
        this_project_redcapfile_latest=project_name+'_latest.csv'
        # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
        df_scan_latest=download_latest_redcapfile(api_token,this_project_redcapfile_latest)
        this_session_redcap_repeat_instance_df=df_scan_latest[df_scan_latest['snipr_session']==session_label]
        this_session_redcap_repeat_instance=str(this_session_redcap_repeat_instance_df['redcap_repeat_instance'].item())
        imaging_data_complete=str(this_session_redcap_repeat_instance_df['imaging_data_complete'].item())
        if imaging_data_complete != '2':
            add_one_file_to_redcap(subject_name,'imaging_data',this_session_redcap_repeat_instance,str('session_pdf'),file_name)
        return 0
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass
    return 1
def fill_redcap_for_pdffile_given_subject_label(subject_name,session_label,project_name,file_name):
    try:
        api_token = os.environ['REDCAP_API']
        this_project_redcapfile_latest=project_name+'_latest.csv'
        df_scan_latest=download_latest_redcapfile(api_token,this_project_redcapfile_latest)
        this_session_redcap_repeat_instance_df=df_scan_latest[df_scan_latest['snipr_session']==session_label]
        this_session_redcap_repeat_instance=str(this_session_redcap_repeat_instance_df['redcap_repeat_instance'].item())
        imaging_data_complete=str(this_session_redcap_repeat_instance_df['imaging_data_complete'].item())
        if imaging_data_complete != '2':
            add_one_file_to_redcap(subject_name,'imaging_data',this_session_redcap_repeat_instance,str('session_pdf'),file_name)
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(api_token), shell=True)
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )

        pass
    return

def decision_which_nifti_used_untilAug62025(sessionId,dir_to_receive_the_data="",output_csvfile=""):
    # sessionId=sys.argv[1]
    # dir_to_receive_the_data="./NIFTIFILEDIR" #sys.argv[2]
    # output_csvfile='test.csv' #sys.argv[3]
    this_session_metadata=get_metadata_session(sessionId)
    jsonStr = json.dumps(this_session_metadata)
    # print(jsonStr)
    df = pd.read_json(jsonStr)
    # # df = pd.read_csv(sessionId+'_scans.csv')
    # sorted_df = df.sort_values(by=['type'], ascending=False)
    # # sorted_df.to_csv('scan_sorted.csv', index=False)
    df_axial_all=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] != 'unusable')] ##| (df['type'] == 'Z-Brain-Thin')]
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] != 'unusable')]
    try:
        if df_axial_all.shape[0]>0:
            df_axial_all_num_usable = df_axial_all[df_axial_all['quality'] == 'usable' ].shape[0]
            if df_axial_all_num_usable.shape[0]>0:
                df_axial=df_axial_all_num_usable
    except:
        pass
    df_thin_all=df.loc[(df['type'] == 'Z-Brain-Thin')  & (df['quality'] != 'unusable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin')  & (df['quality'] != 'unusable') ]
    try:
        if df_thin_all.shape[0]>0:
            df_thin_all_num_usable = df_thin_all[df_thin_all['quality'] == 'usable' ].shape[0]
            if df_thin_all_num_usable.shape[0]>0:
                df_thin=df_thin_all_num_usable
    except:
        pass
    # print(df_axial)
    list_of_usables=[]
    list_of_usables_withsize=[]
    if len(df_axial)>0:
        selectedFile=""
        # print(len(df_axial))
        # print("df_axial:{}".format(len(df_axial['URI'])))
        for item_id, each_axial in df_axial.iterrows():
            print(each_axial['URI'])
            URI=each_axial['URI']
            resource_dir='NIFTI'
            nifti_metadata=json.dumps(get_resourcefiles_metadata(URI,resource_dir)) #get_niftifiles_metadata(each_axial['URI'] )) get_resourcefiles_metadata(URI,resource_dir)
            df_scan = pd.read_json(nifti_metadata)

            for each_item_id,each_nifti in df_scan.iterrows():
                print(each_nifti['URI'])
                if '.nii' in each_nifti['Name'] or '.nii.gz' in each_nifti['Name']:
                    list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID']])
                    x=[each_nifti['URI'],each_nifti['Name'],each_axial['ID']]
                    downloadniftiwithuri(x,dir_to_receive_the_data)
                    number_slice=nifti_number_slice(os.path.join(dir_to_receive_the_data,x[1]))
                    if number_slice <=250 : # and number_slice <=100:
                    # df_maxes=df[df.eval("NUMBEROFSLICES >=20 & (NUMBEROFSLICES <=70)" )]
                        list_of_usables_withsize.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID'],number_slice])
                    # deleteafile(os.path.join(dir_to_receive_the_data,x[1]))



            # break
    elif len(df_thin)>0:
        selectedFile=""
        # print(len(df_axial))
        # print("df_axial:{}".format(len(df_axial['URI'])))
        for item_id, each_thin in df_thin.iterrows():
            print(each_thin['URI'])
            URI=each_thin['URI']
            resource_dir='NIFTI'
            nifti_metadata=json.dumps(get_resourcefiles_metadata(URI,resource_dir)) #json.dumps(get_niftifiles_metadata(each_thin['URI'] ))
            df_scan = pd.read_json(nifti_metadata)

            for each_item_id,each_nifti in df_scan.iterrows():
                # print(each_nifti['URI'])
                if '.nii' in each_nifti['Name'] or '.nii.gz' in each_nifti['Name']:
                    x=[each_nifti['URI'],each_nifti['Name'],each_thin['ID']]
                    list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_thin['ID']])
                    x=[each_nifti['URI'],each_nifti['Name'],each_thin['ID']]
                    downloadniftiwithuri(x,dir_to_receive_the_data)
                    number_slice=nifti_number_slice(os.path.join(dir_to_receive_the_data,x[1]))
                    if  number_slice <=250:
                        list_of_usables_withsize.append([each_nifti['URI'],each_nifti['Name'],each_thin['ID'],number_slice])
                    # print("number_slice:{}".format(number_slice))

                    # deleteafile(os.path.join(dir_to_receive_the_data,x[1]))

            # break
    # dir_to_receive_the_data="./NIFTIFILEDIR"
    # final_ct_file=list_of_usables[0]
    if len(list_of_usables_withsize) > 0:
        jsonStr = json.dumps(list_of_usables_withsize)
        # print(jsonStr)
        df = pd.read_json(jsonStr)
        df.columns=['URI','Name','ID','NUMBEROFSLICES']
        # df_maxes = df[df['NUMBEROFSLICES']>=20 & df['NUMBEROFSLICES']<=65]
        # df=df[df.eval("NUMBEROFSLICES >=20 & (NUMBEROFSLICES <=70)" )]
        # print("df_maxes::{}".format(df_maxes))
        df_maxes = df[df['NUMBEROFSLICES']==df['NUMBEROFSLICES'].max()]

        # return df_maxes
        final_ct_file=''
        if df_maxes.shape[0]>0:
            final_ct_file=df_maxes.iloc[0]
            for item_id, each_scan in df_maxes.iterrows():
                if "tilt" in each_scan['Name']:
                    final_ct_file=each_scan
                    break
        if len(final_ct_file)> 1:
            final_ct_file_df=pd.DataFrame(final_ct_file)
            # pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
            final_ct_file_df.T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
            # now=time.localtime()
            # date_time = time.strftime("_%m_%d_%Y",now)
            print("final_ct_file_df::{}".format(final_ct_file_df.T))
            for final_ct_file_df_item_id, final_ct_file_df_each_scan in final_ct_file_df.T.iterrows():
                # if final_ct_file_df_each_scan['NUMBEROFSLICES'] >= 20 and final_ct_file_df_each_scan['NUMBEROFSLICES'] <= 65:

                niftifile_location=os.path.join(dir_to_receive_the_data,final_ct_file_df_each_scan['Name'].split(".nii")[0]+"_NIFTILOCATION.csv")
                # pd.DataFrame(final_ct_file)
                final_ct_file_df.T.to_csv(niftifile_location,index=False)
                ####################################################

                # now=time.localtime()
                # date_time = time.strftime("_%m_%d_%Y",now)
                # niftifile_location=os.path.join("/output","NIFTIFILE_LOCATION"+"_" +sessionId+"_" +scanId+date_time+".csv")
                # df_listfile.to_csv(niftifile_location,index=False)

                resource_dirname="NIFTI_LOCATION"
                url = (("/data/experiments/%s") % (sessionId))
                uploadsinglefile_with_URI(url,niftifile_location,resource_dirname)
                print("final_ct_file_df::{}".format(final_ct_file_df.T))

            ########################################################
                # try:
                #     fill_redcap_for_selected_scan()
                # except:
                #     pass
                return True
        return False
    else:
        return False


def decision_which_nifti(sessionId, dir_to_receive_the_data="", output_csvfile=""):
    def get_best_from_df(df, slice_order='max'):
        candidates = []

        for _, row in df.iterrows():
            URI = row['URI']
            scan_id = row['ID']
            resource_dir = "NIFTI"
            nifti_meta = json.dumps(get_resourcefiles_metadata(URI, resource_dir))
            df_nifti = pd.read_json(nifti_meta)
            for _, nifti in df_nifti.iterrows():
                if ".nii" in nifti["Name"] or ".nii.gz" in nifti["Name"]:
                    downloadniftiwithuri([nifti["URI"], nifti["Name"], scan_id], dir_to_receive_the_data)
                    path = os.path.join(dir_to_receive_the_data, nifti["Name"])
                    num_slices = nifti_number_slice(path)
                    candidates.append([nifti["URI"], nifti["Name"], scan_id, num_slices])
        if not candidates:
            return None
        df_cand = pd.DataFrame(candidates, columns=["URI", "Name", "ID", "NUMBEROFSLICES"])
        if slice_order == 'max':
            selected = df_cand[df_cand["NUMBEROFSLICES"] == df_cand["NUMBEROFSLICES"].max()]
        else:
            selected = df_cand[df_cand["NUMBEROFSLICES"] == df_cand["NUMBEROFSLICES"].min()]
        return selected.iloc[0] if not selected.empty else None

    # Load session metadata
    this_session_metadata = get_metadata_session(sessionId)
    df = pd.read_json(json.dumps(this_session_metadata))

    # Categorize scans
    axial_usable = df[(df['type'] == 'Z-Axial-Brain') & (df['quality'] == 'usable')]
    axial_questionable = df[(df['type'] == 'Z-Axial-Brain') & (df['quality'] == 'questionable')]
    thin_usable = df[(df['type'] == 'Z-Brain-Thin') & (df['quality'] == 'usable')]
    thin_questionable = df[(df['type'] == 'Z-Brain-Thin') & (df['quality'] == 'questionable')]
    # Collect counts
    category_counts = {
        "axial_usable": len(axial_usable),
        "axial_questionable": len(axial_questionable),
        "thin_usable": len(thin_usable),
        "thin_questionable": len(thin_questionable),
    }

    # Convert to DataFrame
    summary_df = pd.DataFrame(list(category_counts.items()), columns=["Category", "Count"])

    # Save to CSV
    output_path = "/output/this_session_metadata_count.csv"
    summary_df.to_csv(output_path, index=False)

    # df.to_csv('/output/this_session_metadata_1.csv',index=False)
    # Apply decision logic
    selected_scan = None
    if not axial_usable.empty:
        selected_scan = get_best_from_df(axial_usable, slice_order='max')
    elif  not thin_usable.empty:
        if not axial_questionable.empty:
            selected_scan = get_best_from_df(axial_questionable, slice_order='max')

        else:
            selected_scan = get_best_from_df(thin_usable, slice_order='min')
    elif not axial_questionable.empty:
        selected_scan = get_best_from_df(axial_questionable, slice_order='max')

    elif not thin_questionable.empty:
        selected_scan = get_best_from_df(thin_questionable, slice_order='min')

    else:
        print("No scan selected")

        return False

    # Export and upload
    if selected_scan is not None:
        df_final = pd.DataFrame([selected_scan])
        df_final.to_csv(os.path.join(dir_to_receive_the_data, output_csvfile), index=False)

        niftifile_location = os.path.join(
            dir_to_receive_the_data,
            selected_scan["Name"].split(".nii")[0] + "_NIFTILOCATION.csv"
        )
        df_final.to_csv(niftifile_location, index=False)

        resource_dirname = "NIFTI_LOCATION"
        url = f"/data/experiments/{sessionId}"
        uploadsinglefile_with_URI(url, niftifile_location, resource_dirname)
        return True

    return False

def nifti_number_slice(niftifilename):
    return nib.load(niftifilename).shape[2]

    # pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
# def downloadniftiwithuri(URI,dir_to_save,niftioutput_filename):
#     #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
#     # for x in range(df.shape[0]):
#     #     print(df.iloc[x])

#     url =   URI #  df.iloc[0][0] #URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" %
#         # (sessionId, scanId))
#     print(url)
#     #xnatSession.renew_httpsession()
#     response = xnatSession.httpsess.get(xnatSession.host + url)
#     zipfilename=os.path.join(dir_to_save,niftioutput_filename) #sessionId+scanId+'.zip'
#     with open(zipfilename, "wb") as f:
#         for chunk in response.iter_content(chunk_size=512):
#             if chunk:  # filter out keep-alive new chunks
#                 f.write(chunk)
#     #xnatSession.close_httpsession())

# def get_urls_csvfiles_in_EDEMA_BIOMARKER_inaproject(sessions_list):
#     jsonStr = json.dumps(sessions_list)
#     # print(jsonStr)
#     df = pd.read_json(jsonStr)
#     for item_id, each_session in df_touse.iterrows():
#         sessionId=each_session['ID']
#         this_session_metadata=get_metadata_session(sessionId)


#     this_session_metadata=get_metadata_session(sessionId)
#     jsonStr = json.dumps(this_session_metadata)
#     # print(jsonStr)
#     df = pd.read_json(jsonStr)
#     df_touse=df.loc[(df['ID'] == int(scanId))]

#     # print("get_resourcefiles_metadata(df_touse['URI'],resource_foldername ){}".format(get_resourcefiles_metadata(df_touse['URI'],resource_foldername )))
#     for item_id, each_scan in df_touse.iterrows():
#         print("each_scan['URI'] {}".format(each_scan['URI']))
#         nifti_metadata=json.dumps(get_resourcefiles_metadata(each_scan['URI'],resource_foldername ))
#         df_scan = pd.read_json(nifti_metadata)
#         pd.DataFrame(df_scan).to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)


def get_maskfile_scan_metadata():
    sessionId=sys.argv[1]
    scanId=sys.argv[2]
    resource_foldername=sys.argv[3]
    dir_to_receive_the_data=sys.argv[4]
    output_csvfile=sys.argv[5]
    this_session_metadata=get_metadata_session(sessionId)
    jsonStr = json.dumps(this_session_metadata)
    # print(jsonStr)
    df = pd.read_json(jsonStr)
    df_touse=df.loc[(df['ID'] == int(scanId))]

    # print("get_resourcefiles_metadata(df_touse['URI'],resource_foldername ){}".format(get_resourcefiles_metadata(df_touse['URI'],resource_foldername )))
    for item_id, each_scan in df_touse.iterrows():
        print("each_scan['URI'] {}".format(each_scan['URI']))
        nifti_metadata=json.dumps(get_resourcefiles_metadata(each_scan['URI'],resource_foldername ))
        df_scan = pd.read_json(nifti_metadata)
        pd.DataFrame(df_scan).to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
def get_relevantfile_from_NIFTIDIR():
    sessionId=sys.argv[1]
    dir_to_receive_the_data=sys.argv[2]
    output_csvfile=sys.argv[3]
    this_session_metadata=get_metadata_session(sessionId)
    jsonStr = json.dumps(this_session_metadata)
    # print(jsonStr)
    df = pd.read_json(jsonStr)
    # # df = pd.read_csv(sessionId+'_scans.csv')
    # sorted_df = df.sort_values(by=['type'], ascending=False)
    # # sorted_df.to_csv('scan_sorted.csv', index=False)
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] != 'unusable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin') & (df['quality'] != 'unusable')] ##| (df['type'] == 'Z-Brain-Thin')]
    # print(df_axial)
    list_of_usables=[]
    if len(df_axial)>0:
        selectedFile=""
        # print(len(df_axial))
        # print("df_axial:{}".format(len(df_axial['URI'])))
        for item_id, each_axial in df_axial.iterrows():
            print(each_axial['URI'])
            nifti_metadata=json.dumps(get_niftifiles_metadata(each_axial['URI'] ))
            df_scan = pd.read_json(nifti_metadata)

            for each_item_id,each_nifti in df_scan.iterrows():
                print(each_nifti['URI'])
                list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID']])
            break
    elif len(df_thin)>0:
        selectedFile=""
        # print(len(df_axial))
        # print("df_axial:{}".format(len(df_axial['URI'])))
        for item_id, each_thin in df_thin.iterrows():
            print(each_thin['URI'])
            nifti_metadata=json.dumps(get_niftifiles_metadata(each_thin['URI'] ))
            df_scan = pd.read_json(nifti_metadata)

            for each_item_id,each_nifti in df_scan.iterrows():
                print(each_nifti['URI'])
                list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_thin['ID']])
            break
    final_ct_file=list_of_usables[0]
    for x in list_of_usables:
        if "tilt" in x[0].lower():
            final_ct_file=x
            break
    # downloadniftiwithuri(final_ct_file,dir_to_receive_the_data)
    pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)

def downloadniftiwithuri_withcsv():
    csvfilename=sys.argv[1]
    dir_to_save=sys.argv[2]
    df=pd.read_csv(csvfilename)
    print('csvfilename::{}::dir_to_save::{}'.format(csvfilename,dir_to_save))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    for x in range(df.shape[0]):
        print(df.iloc[x])

        url =     df.iloc[x][0] #URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" %
            # (sessionId, scanId))
        print(url)
        #xnatSession.renew_httpsession()
        response = xnatSession.httpsess.get(xnatSession.host + url)
        zipfilename=os.path.join(dir_to_save,df.iloc[x][1]) #sessionId+scanId+'.zip'
        with open(zipfilename, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        #xnatSession.close_httpsession())

def downloadmaskswithuri_withcsv():
    csvfilename=sys.argv[1]
    dir_to_save=sys.argv[2]
    df=pd.read_csv(csvfilename)
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    for item_id, each_scan in df.iterrows():
        # print("each_scan['URI'] {}".format(each_scan['URI']))
    # for x in range(df.shape[0]):
        # print(df.iloc[x])

        url =  each_scan['URI'] #   df.iloc[0][0] #URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" %
            # (sessionId, scanId))
        print(url)
        #xnatSession.renew_httpsession()
        response = xnatSession.httpsess.get(xnatSession.host + url)
        zipfilename=os.path.join(dir_to_save,each_scan['Name']) #sessionId+scanId+'.zip'
        with open(zipfilename, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        #xnatSession.close_httpsession())
def downloadresourcefilewithuri_py(url,dir_to_save):
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url['URI'])
    zipfilename=os.path.join(dir_to_save,url['Name']) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    #xnatSession.close_httpsession())
def dowload_a_folder_as_zip(sessionId, scanId,resource_dir):
    ##xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    try:
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        url = ("/data/experiments/%s/scans/%s/resources/%s/files?format=zip" %
               (sessionId, scanId,resource_dir))

        #xnatSession.renew_httpsession()
        response = xnatSession.httpsess.get(xnatSession.host + url)
        zipfilename=os.path.join('/workinginput',sessionId+scanId+resource_dir+'.zip')
        with open(zipfilename, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        command = 'unzip -d /ZIPFILEDIR ' + zipfilename
        subprocess.call(command,shell=True)
        # command='rm -r ' + zipfilename
        # command = 'unzip -d /ZIPFILEDIR ' + zipfilename
        # subprocess.call(command,shell=True)
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        return True
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
def call_dowload_a_folder_as_zip(args):
    try:
        sessionId=args.stuff[1]
        scanId=args.stuff[2]
        resource_dir=args.stuff[3]
        dowload_a_folder_as_zip(sessionId, scanId,resource_dir)
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
def downloadniftiwithuri(URI_name,dir_to_save):
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    url = URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" %
        # (sessionId, scanId))
    print(url)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    zipfilename=os.path.join(dir_to_save,URI_name[1]) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    #xnatSession.close_httpsession())

def get_niftifiles_metadata(URI):
    url = (URI+'/resources/NIFTI/files?format=json')
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_nifti=response.json()['ResultSet']['Result']
    return metadata_nifti
def get_resourcefiles_metadata(URI,resource_dir):
    url = (URI+'/resources/' + resource_dir +'/files?format=json')
    print(url)
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_masks=response.json()['ResultSet']['Result']
    return metadata_masks
def get_resourcefiles_metadata_saveascsv(URI,resource_dir,dir_to_receive_the_data,output_csvfile):

    url = (URI+'/resources/' + resource_dir +'/files?format=json')
    # print("url::{}".format(url))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_masks=response.json()['ResultSet']['Result']
    # print("metadata_masks::{}".format(metadata_masks))
    df_scan = pd.read_json(json.dumps(metadata_masks))
    pd.DataFrame(df_scan).to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
    # return metadata_masks
def call_get_resourcefiles_metadata_saveascsv():
    try:
        URI=sys.argv[1]
        # print("URI::{}".format(URI))
        URI=URI.split('/resources')[0]
        # print("URI::{}".format(URI))
        resource_dir=sys.argv[2]
        dir_to_receive_the_data=sys.argv[3]
        output_csvfile=sys.argv[4]
        get_resourcefiles_metadata_saveascsv(URI,resource_dir,dir_to_receive_the_data,output_csvfile)
        print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
    return 0

def call_get_resourcefiles_metadata_saveascsv_args(args):
    try:
        URI=args.stuff[1] #sys.argv[1]
        # print("URI::{}".format(URI))
        URI=URI.split('/resources')[0]
        # print("URI::{}".format(URI))
        resource_dir=args.stuff[2] #sys.argv[2]
        dir_to_receive_the_data=args.stuff[3] #sys.argv[3]
        output_csvfile=args.stuff[4] #sys.argv[4]
        get_resourcefiles_metadata_saveascsv(URI,resource_dir,dir_to_receive_the_data,output_csvfile)
        print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
    return 0
def findthetargetscan():
     target_scan=""
     ## find the list of usable scans
     ## Is axial available? If yes, focus on axial, if not go for thin
     ## Is tilt available ? If yes, get the tilt, if not go for non-tilt
     return target_scan
def downloadfile_withasuffix(sessionId,scanId,output_dirname,resource_dirname,file_suffix):
    try:

        # print('sessionId::scanId::resource_dirname::output_dirname::{}::{}::{}::{}'.format(sessionId,scanId,resource_dirname,output_dirname))
        url = (("/data/experiments/%s/scans/%s/resources/"+resource_dirname+"/files/") % (sessionId, scanId))
        df_listfile=listoffile_witha_URI_as_df(url)
        for item_id, row in df_listfile.iterrows():
            if file_suffix in str(row['URI']) : ##.str.contains(file_suffix):
                download_a_singlefile_with_URIString(row['URI'],row['Name'],output_dirname)
                print("DOWNLOADED ::{}".format(row))

        return True
    except Exception as exception:
        print("FAILED AT ::{}".format(exception))
        pass
    return  False
def downloadfile_session_withasuffix(sessionId,output_dirname,resource_dirname,file_suffix):
    try:

        # print('sessionId::scanId::resource_dirname::output_dirname::{}::{}::{}::{}'.format(sessionId,scanId,resource_dirname,output_dirname))
        url = (("/data/experiments/%s/resources/"+resource_dirname+"/files/") % (sessionId))
        df_listfile=listoffile_witha_URI_as_df(url)
        for item_id, row in df_listfile.iterrows():
            if file_suffix in str(row['URI']) : ##.str.contains(file_suffix):
                download_a_singlefile_with_URIString(row['URI'],row['Name'],output_dirname)
                print("DOWNLOADED ::{}".format(row))

        return True
    except Exception as exception:
        print("FAILED AT ::{}".format(exception))
        pass
    return  False

def uploadfile():
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    input_dirname=str(sys.argv[3])
    resource_dirname=str(sys.argv[4])
    file_suffix=str(sys.argv[5])
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    url = (("/data/experiments/%s/scans/%s/resources/"+resource_dirname+"/files/") % (sessionId, scanId))
    allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
    for eachniftifile in allniftifiles:
        files={'file':open(eachniftifile,'rb')}
        response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
        print(response)
    #xnatSession.close_httpsession())
    # for eachniftifile in allniftifiles:
    #     command= 'rm  ' + eachniftifile
    #     subprocess.call(command,shell=True)
    return True

def uploadfile_withprefix():
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    input_dirname=str(sys.argv[3])
    resource_dirname=str(sys.argv[4])
    file_suffix=str(sys.argv[5])
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    url = (("/data/experiments/%s/scans/%s/resources/"+resource_dirname+"/files/") % (sessionId, scanId))
    allniftifiles=glob.glob(os.path.join(input_dirname,file_suffix+'*') ) #input_dirname + '/*'+file_suffix)
    for eachniftifile in allniftifiles:
        files={'file':open(eachniftifile,'rb')}
        response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
        print(response)
    #xnatSession.close_httpsession())
    # for eachniftifile in allniftifiles:
    #     command= 'rm  ' + eachniftifile
    #     subprocess.call(command,shell=True)
    return True
def uploadsinglefile():
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    input_dirname=str(sys.argv[3])
    resource_dirname=str(sys.argv[4])
    file_name=str(sys.argv[5])
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    url = (("/data/experiments/%s/scans/%s/resources/"+resource_dirname+"/files/") % (sessionId, scanId))
    # allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
    # for eachniftifile in allniftifiles:
    eachniftifile=os.path.join(input_dirname,file_name)
    files={'file':open(eachniftifile,'rb')}
    response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
    print(response)
    #xnatSession.close_httpsession())
    # for eachniftifile in allniftifiles:
    #     command= 'rm  ' + eachniftifile
    #     subprocess.call(command,shell=True)
    return True
def uploadsinglefile_X_level(X_level,projectId,eachniftifile,resource_dirname):
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    url = (("/data/"+X_level+"/%s/resources/"+resource_dirname+"/files/") % (projectId))
    files={'file':open(eachniftifile,'rb')}
    response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
    print(response)
    #xnatSession.close_httpsession())

def uploadfile_projectlevel():
    try:
        projectId=str(sys.argv[1])
        input_dirname=str(sys.argv[2])
        resource_dirname=str(sys.argv[3])
        file_suffix=str(sys.argv[4])
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        url = (("/data/projects/%s/resources/"+resource_dirname+"/files/") % (projectId))
        allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
        for eachniftifile in allniftifiles:
            files={'file':open(eachniftifile,'rb')}
            response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
            print(response)
        #xnatSession.close_httpsession())
        # for eachniftifile in allniftifiles:
        #     command= 'rm  ' + eachniftifile
        #     subprocess.call(command,shell=True)
        return True
    except Exception as e:
        print(e)
        return False
def call_uploadsinglefile_with_URI(args):
    url=args.stuff[1]
    file_name=args.stuff[2]
    resource_dirname=args.stuff[3]
    # url=args.stuff[1]
    uploadsinglefile_with_URI(url,file_name,resource_dirname)

def uploadsinglefile_with_URI(url,file_name,resource_dirname):
    try:

        url = url+"/resources/"+resource_dirname+"/files/"
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        files={'file':open(file_name,'rb')}
        response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
        print("response::{}".format(response))

        #xnatSession.close_httpsession())
        print("I UPLOADED FILE WITH  uploadsinglefile_with_URI")
    except:
        print("I FAILED AT uploadsinglefile_with_URI")
        pass

def uploadfilesfromlistinacsv(urllistfilename,X_level,projectId,resource_dirname):
    try:
        urllistfilename_df=pd.read_csv(urllistfilename)
        for item_id, row in urllistfilename_df.iterrows():
            eachniftifile=row['LOCAL_FILENAME']
            # print("eachniftifile_ROW::{}".format(row))
            uploadsinglefile_X_level(X_level,projectId,eachniftifile,resource_dirname)
            print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
        return 1 #print("ROW::{}".format(row['LOCAL_FILENAME'])) #print("X_level::{}::projectId::{}::eachniftifile::{}::resource_dirname::{}".format(X_level,projectId,eachniftifile,resource_dirname))
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
    return 0

def call_uploadfilesfromlistinacsv(args):
    urllistfilename=args.stuff[1]
    X_level=args.stuff[2]
    projectId=args.stuff[3]
    resource_dirname=args.stuff[4]
    uploadfilesfromlistinacsv(urllistfilename,X_level,projectId,resource_dirname)
def uploadsinglefile_projectlevel_args(args):
    try:
        projectId=args.stuff[1] #str(sys.argv[1])
        input_dirname=args.stuff[2] #str(sys.argv[2])
        resource_dirname=args.stuff[3] #str(sys.argv[3])
        file_name=args.stuff[4] # str(sys.argv[4])
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        url = (("/data/projects/%s/resources/"+resource_dirname+"/files/") % (projectId))
        # allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
        eachniftifile=os.path.join(input_dirname,file_name)
        files={'file':open(eachniftifile,'rb')}
        # for eachniftifile in allniftifiles:
        #     files={'file':open(eachniftifile,'rb')}
        response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
        print(response)
        #xnatSession.close_httpsession())
        # for eachniftifile in allniftifiles:
        #     command= 'rm  ' + eachniftifile
        #     subprocess.call(command,shell=True)
        return True
    except Exception as e:
        print(e)
        return False
def uploadsinglefile_projectlevel():
    try:
        projectId=str(sys.argv[1])
        input_dirname=str(sys.argv[2])
        resource_dirname=str(sys.argv[3])
        file_name=str(sys.argv[4])
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        url = (("/data/projects/%s/resources/"+resource_dirname+"/files/") % (projectId))
        # allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
        eachniftifile=os.path.join(input_dirname,file_name)
        files={'file':open(eachniftifile,'rb')}
        # for eachniftifile in allniftifiles:
        #     files={'file':open(eachniftifile,'rb')}
        response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
        print(response)
        #xnatSession.close_httpsession())
        # for eachniftifile in allniftifiles:
        #     command= 'rm  ' + eachniftifile
        #     subprocess.call(command,shell=True)
        return True
    except Exception as e:
        print(e)
        return False
def downloadandcopyfile():
    sessionId=sys.argv[1]
    scanId=sys.argv[2]
    metadata_session=get_metadata_session(sessionId)
    decision=decide_image_conversion(metadata_session,scanId)
    command= 'rm -r /ZIPFILEDIR/*'
    subprocess.call(command,shell=True)
    if decision==True:
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        outcome=get_nifti_using_xnat(sessionId, scanId)
        if outcome==False:
            print("NO DICOM FILE %s:%s:%s:%s" % (sessionId, scanId))
        #xnatSession.close_httpsession())
        try :
            copy_nifti()
            print("COPIED TO WORKINGDIRECTORY")
        except:
            pass
def downloadandcopyallniftifiles():
    sessionId=sys.argv[1]
    scanId=sys.argv[2]
    metadata_session=get_metadata_session(sessionId)
    # decision=decide_image_conversion(metadata_session,scanId)
    command= 'rm -r /ZIPFILEDIR/*'
    subprocess.call(command,shell=True)
    # if decision==True:
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    outcome=get_nifti_using_xnat(sessionId, scanId)
    if outcome==False:
        print("NO DICOM FILE %s:%s:%s:%s" % (sessionId, scanId))
    #xnatSession.close_httpsession())
    try :
        copy_nifti()
        print("COPIED TO WORKINGDIRECTORY")
    except:
        pass
def copy_nifti():
    for dirpath, dirnames, files in os.walk('/ZIPFILEDIR'):
    #                print(f'Found directory: {dirpath}')
        for file_name in files:
            file_extension = pathlib.Path(file_name).suffix
            if 'nii' in file_extension:
                command='cp ' + os.path.join(dirpath,file_name) + '  /workinginput/'
                subprocess.call(command,shell=True)
                print(os.path.join(dirpath,file_name))




def get_slice_idx(nDicomFiles):
    return min(nDicomFiles-1, math.ceil(nDicomFiles*0.7)) # slice 70% through the brain
def get_metadata_subject(project_id,subject_id,outputfile="NONE.csv"):
    url = ("/data/projects/%s/subjects/%s/experiments/?format=json" %    (project_id,subject_id))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_subj=response.json()['ResultSet']['Result']
    metadata_subj_1=json.dumps(metadata_subj)
    df_scan = pd.read_json(metadata_subj_1)
    df_scan.to_csv(outputfile,index=False)
    return metadata_subj
def get_metadata_session(sessionId,outputfile="NONE.csv"):
    url = ("/data/experiments/%s/scans/?format=json" %    (sessionId))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_session=response.json()['ResultSet']['Result']
    metadata_session_1=json.dumps(metadata_session)
    df_scan = pd.read_json(metadata_session_1)
    df_scan.to_csv(outputfile,index=False)
    return metadata_session
def get_metadata_project_sessionlist(project_ID,outputfile="NONE.csv"):
    url = ("/data/projects/%s/experiments/?format=json" %    (project_ID))
    # /data/projects/${project_ID}/experiments/
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_session=response.json()['ResultSet']['Result']
    metadata_session_1=json.dumps(metadata_session)
    df_scan = pd.read_json(metadata_session_1)
    df_scan.to_csv(outputfile,index=False)
    return metadata_session
def get_session_label(sessionId,outputfile="NONE.csv"):
    returnvalue=''
    try:
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        # sessionId='SNIPR02_E02933'

        url = ("/data/experiments/%s/?format=json" %    (sessionId)) #scans/
        response = xnatSession.httpsess.get(xnatSession.host + url)
        #xnatSession.close_httpsession())
        session_label=response.json()['items'][0]['data_fields']['label']
        df_session=pd.DataFrame([session_label])
        df_session.columns=['SESSION_LABEL']
        df_session.to_csv(outputfile,index=False)
        command="echo successful at :: {}::maskfilename::{} >> /software/error.txt".format(inspect.stack()[0][3],'get_session_label')
        subprocess.call(command,shell=True)
        returnvalue=session_label
    except:
        command="echo failed at :: {} >> /software/error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return returnvalue
def get_session_project(sessionId,outputfile="NONE.csv"):
    returnvalue=''
    try:
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        # sessionId='SNIPR02_E02933'

        url = ("/data/experiments/%s/?format=json" %    (sessionId)) #scans/
        response = xnatSession.httpsess.get(xnatSession.host + url)
        #xnatSession.close_httpsession())
        session_label=response.json()['items'][0]['data_fields']['project']
        df_session=pd.DataFrame([session_label])
        df_session.columns=['SESSION_PROJECT']
        df_session.to_csv(outputfile,index=False)
        command="echo successful at :: {}::maskfilename::{} >> /software/error.txt".format(inspect.stack()[0][3],'get_session_project')
        subprocess.call(command,shell=True)
        returnvalue=session_label
    except:
        command="echo failed at :: {} >> /software/error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return returnvalue


def call_get_session_label(args):
    returnvalue=0
    try:
        sessionId=args.stuff[1]
        outputfile=args.stuff[2]
        get_session_label(sessionId,outputfile=outputfile)
        command="echo successful at :: {}::maskfilename::{} >> /software/error.txt".format(inspect.stack()[0][3],'call_get_metadata_session')
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> /software/error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return returnvalue
def call_get_session_project(args):
    returnvalue=0
    try:
        sessionId=args.stuff[1]
        outputfile=args.stuff[2]
        get_session_project(sessionId,outputfile=outputfile)
        command="echo successful at :: {}::maskfilename::{} >> /software/error.txt".format(inspect.stack()[0][3],'call_get_session_project')
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> /software/error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return returnvalue


def call_get_metadata_session(args):
    returnvalue=0
    try:
        outpufilename=""
        sessionId=args.stuff[1]
        try:
            outpufilename=args.stuff[2]
        except:
            pass
        if len(outpufilename)>0:
            get_metadata_session(sessionId,outpufilename)
        else:
            get_metadata_session(sessionId)
        command="echo successful at :: {}::maskfilename::{} >> /software/error.txt".format(inspect.stack()[0][3],'call_get_metadata_session')
        subprocess.call(command,shell=True)
        returnvalue=1
    except:
        command="echo failed at :: {} >> /software/error.txt".format(inspect.stack()[0][3])
        subprocess.call(command,shell=True)
    return returnvalue
def get_metadata_session_forbash():
    sessionId=sys.argv[1]
    url = ("/data/experiments/%s/scans/?format=json" %    (sessionId))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    #xnatSession.close_httpsession())
    metadata_session=response.json()['ResultSet']['Result']
    print(metadata_session)
    data_file = open('this_sessionmetadata.csv', 'w')
    csv_writer = csv.writer(data_file)
    count = 0
    for data in metadata_session:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())
    data_file.close()
    return metadata_session
def decide_image_conversion(metadata_session,scanId):
    decision=False
    usable=False
    brain_type=False
    for x in metadata_session:
        if x['ID']  == scanId:
            print(x['ID'])
            # result_usability = response.json()['ResultSet']['Result'][0]['quality']
            result_usability = x['quality']
#             print(result)
            if 'unusable' not in result_usability.lower():
                print(True)
                usable=True
            result_type= x['type']
            if 'z-axial-brain' in result_type.lower() or 'z-brain-thin' in result_type.lower():
                print(True)
                brain_type=True
            break
    if usable==True and brain_type==True:
        decision =True
    return decision




# result = response.json()['ResultSet']['Result']
# # print(result[0]) #['absolutePath'])
# nDicomFiles = len(result)
# # print(nDicomFiles)
# if nDicomFiles == 0:
#     raise Exception("No DICOM files for %s stored in XNAT" % scanId)


def get_nifti_using_xnat(sessionId, scanId):
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    url = ("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" %
        (sessionId, scanId))

    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    zipfilename=os.path.join('/workinginput',sessionId+scanId+'.zip')
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    command = 'unzip -d /ZIPFILEDIR ' + zipfilename
    subprocess.call(command,shell=True)
    command='rm -r ' + zipfilename
    command = 'unzip -d /ZIPFILEDIR ' + zipfilename
    subprocess.call(command,shell=True)

    return True
def call_downloadfiletolocaldir_py(args):
    sessionId=args.stuff[1]
    scanId=args.stuff[2]
    resource_dirname=args.stuff[3]
    output_dirname=args.stuff[4]
    downloadfiletolocaldir_py(sessionId,scanId,resource_dirname,output_dirname)
def downloadfiletolocaldir_py(sessionId,scanId,resource_dirname,output_dirname):
    # print(sys.argv)
    # sessionId=str(sys.argv[1])
    # scanId=str(sys.argv[2])
    # resource_dirname=str(sys.argv[3])
    # output_dirname=str(sys.argv[4])

    print('sessionId::scanId::resource_dirname::output_dirname::{}::{}::{}::{}'.format(sessionId,scanId,resource_dirname,output_dirname))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    resource_dir_url=(("/data/experiments/%s/scans/%s")  %
                      (sessionId, scanId))
    print('resource_dir_url::{}'.format(resource_dir_url))
    # resource_metadata=get_resourcefiles_metadata(resource_dir_url,resource_dirname)
    # df_scan = pd.read_json(json.dumps(resource_metadata))
    # print('df_scan::{}'.format(resource_metadata))
    url = (("/data/experiments/%s/scans/%s/resources/" + resource_dirname+ "/files?format=zip")  %
           (sessionId, scanId))

    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    zipfilename=sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    command='rm -r /ZIPFILEDIR/* '
    subprocess.call(command,shell=True)
    command = 'unzip -d /ZIPFILEDIR ' + zipfilename
    subprocess.call(command,shell=True)
    #xnatSession.close_httpsession())
    copy_nifti_to_a_dir(output_dirname)
    copy_mat_to_a_dir(output_dirname)
    copy_allfile_to_a_dir(output_dirname)

    return True


def downloadfiletolocaldir():
    print(sys.argv)
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    resource_dirname=str(sys.argv[3])
    output_dirname=str(sys.argv[4])

    print('sessionId::scanId::resource_dirname::output_dirname::{}::{}::{}::{}'.format(sessionId,scanId,resource_dirname,output_dirname))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    resource_dir_url=(("/data/experiments/%s/scans/%s")  %
        (sessionId, scanId))
    print('resource_dir_url::{}'.format(resource_dir_url))
    # resource_metadata=get_resourcefiles_metadata(resource_dir_url,resource_dirname)
    # df_scan = pd.read_json(json.dumps(resource_metadata))
    # print('df_scan::{}'.format(resource_metadata))
    url = (("/data/experiments/%s/scans/%s/resources/" + resource_dirname+ "/files?format=zip")  %
        (sessionId, scanId))

    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    zipfilename=sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    command='rm -r /ZIPFILEDIR/* '
    subprocess.call(command,shell=True)
    command = 'unzip -d /ZIPFILEDIR ' + zipfilename
    subprocess.call(command,shell=True)
    #xnatSession.close_httpsession())
    copy_nifti_to_a_dir(output_dirname)
    copy_mat_to_a_dir(output_dirname)

    return True
# def downloadfiletolocaldir_py(sessionId,scanId,resource_dirname,output_dirname):
#     #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
#     url = (("/data/experiments/%s/scans/%s/resources/" + resource_dirname+ "/files?format=zip")  %
#         (sessionId, scanId))

#     #xnatSession.renew_httpsession()
#     response = xnatSession.httpsess.get(xnatSession.host + url)
#     zipfilename=sessionId+scanId+'.zip'
#     with open(zipfilename, "wb") as f:
#         for chunk in response.iter_content(chunk_size=512):
#             if chunk:  # filter out keep-alive new chunks
#                 f.write(chunk)
#     command='rm -r /ZIPFILEDIR/* '
#     subprocess.call(command,shell=True)
#     command = 'unzip -d /ZIPFILEDIR ' + zipfilename
#     subprocess.call(command,shell=True)
#     #xnatSession.close_httpsession())
#     copy_nifti_to_a_dir(output_dirname)
def copy_allfile_to_a_dir(dir_name):
    for dirpath, dirnames, files in os.walk('/ZIPFILEDIR'):
        #                print(f'Found directory: {dirpath}')
        for file_name in files:
            # file_extension = pathlib.Path(file_name).suffix
        # if  file_extension:
            command='cp ' + os.path.join(dirpath,file_name) + '  ' + dir_name + '/'
            subprocess.call(command,shell=True)
            print(os.path.join(dirpath,file_name))

#     return True
def copy_nifti_to_a_dir(dir_name):
    for dirpath, dirnames, files in os.walk('/ZIPFILEDIR'):
    #                print(f'Found directory: {dirpath}')
        for file_name in files:
            file_extension = pathlib.Path(file_name).suffix
            if 'nii' in file_extension or 'gz' in file_extension:
                command='cp ' + os.path.join(dirpath,file_name) + '  ' + dir_name + '/'
                subprocess.call(command,shell=True)
                print(os.path.join(dirpath,file_name))
def copy_mat_to_a_dir(dir_name):
    for dirpath, dirnames, files in os.walk('/ZIPFILEDIR'):
        #                print(f'Found directory: {dirpath}')
        for file_name in files:
            file_extension = pathlib.Path(file_name).suffix
            if '.mat' in file_extension :
                command='cp ' + os.path.join(dirpath,file_name) + '  ' + dir_name + '/'
                subprocess.call(command,shell=True)
                print(os.path.join(dirpath,file_name))

## load two files:
def list_analyzed_session(pdffilelist_file,selectedniftifilelist_file,allsessionlist_file,output_list_csvfile,pdffilelist_file_ext=".pdf",stringtofilterallsessionlist=''):
    file1=pdffilelist_file #"workingoutput/allfilesinprojectoutput.csv"
    file2=selectedniftifilelist_file #"workingoutput/COLI_EDEMA_BIOMARKER_ANALYZED.csv"
    file3=allsessionlist_file #"workingoutput/all_sessions.csv"
    df1=pd.read_csv(file1)
    df2=pd.read_csv(file2)
    columname='NIFTIFILENAME'
    df1[columname] = df1['Name']
    df1[['NIFTIFILENAME','RESTOFTHENAME']] =df1.NIFTIFILENAME.str.split(pdffilelist_file_ext, expand = True)
    # # aa.to_csv(csvfile,index=False)
    df1=df1[df1['Name'].str.contains('.pdf')]
    df2['SESSION_ID'] = df2['URI'].str.split('/').str[3]
    # # df2['NIFTIFILENAME'] = df2['URI'].str.split('/').str[9].split('.nii')[0]
    columname='NIFTIFILENAME'
    df2[columname] = df2['Name']
    df2[['NIFTIFILENAME','RESTOFTHENAME']] =df2.NIFTIFILENAME.str.split(".nii", expand = True)
    df3 = pd.merge(df1, df2, left_on='NIFTIFILENAME', right_on='NIFTIFILENAME')
    df3=df3[['NIFTIFILENAME','SESSION_ID']]
    df4=pd.read_csv(file3)
    df4=df4[df4['label'].str.contains(stringtofilterallsessionlist)]
    df4['SESSION_NAME']=df4[['label']]
    df4=df4[['ID','SESSION_NAME']]
    # df4=df4[['ID','label']]

    df5 = pd.merge(df4, df3, right_on='SESSION_ID', left_on='ID',how='outer')
    # print(df3.shape)
    # print(df4.shape)
    # print(df5.shape)
    df5['SESSION_ID']=df5[['ID']]
    df5=df5[['SESSION_ID','NIFTIFILENAME','SESSION_NAME']]
    # print(df5)
    df5['ANALYZED']=0
    df5.loc[df5["NIFTIFILENAME"].str.len()>1,'ANALYZED']=1 #.value_counts()
    df5.to_csv(output_list_csvfile,index=False)
    # # df5.loc[df["NIFTIFILENAME"].str.len() > 1 , "gender"] = 1
    print(df5)
def call_list_analyzed_session():
    pdffilelist_file =sys.argv[1] #"workingoutput/allfilesinprojectoutput.csv"
    selectedniftifilelist_file =sys.argv[2]  #"workingoutput/COLI_EDEMA_BIOMARKER_ANALYZED.csv"
    allsessionlist_file = sys.argv[3]  #"workingoutput/all_sessions.csv"
    output_list_csvfile=sys.argv[4]  #"workingoutput/all_sessions_labeled.csv"
    pdffilelist_file_ext=sys.argv[5]
    stringtofilterallsessionlist=sys.argv[6]
    list_analyzed_session(pdffilelist_file,selectedniftifilelist_file,allsessionlist_file,output_list_csvfile,pdffilelist_file_ext,stringtofilterallsessionlist)


def check_if_a_file_exist_in_snipr(URI, resource_dir,extension_to_find_list):
    url = (URI+'/resources/' + resource_dir +'/files?format=json')
    # print("url::{}".format(url))
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    num_files_present=0
    if response.status_code != 200:
        #xnatSession.close_httpsession())
        return num_files_present
    metadata_masks=response.json()['ResultSet']['Result']
    # print("metadata_masks::{}".format(metadata_masks))
    df_scan = pd.read_json(json.dumps(metadata_masks))
    for extension_to_find in extension_to_find_list:
        for x in range(df_scan.shape[0]):
            print(df_scan.loc[x,'Name'])
            if extension_to_find in df_scan.loc[x,'Name']:
                num_files_present=num_files_present+1
                break
    return num_files_present
def print_hosts():
    print(XNAT_HOST)
    print(XNAT_USER)
    print(XNAT_PASS)
    URI="/data/experiments/SNIPR01_E00131/scans/3"
    resource_dir="MASKS"
    extension_to_find_list=["levelset"]
    num_files_present=check_if_a_file_exist_in_snipr(URI, resource_dir,extension_to_find_list)
    if num_files_present < len(extension_to_find_list):
        print("REQUIRED NUMBER OF FILES NOT PRESENT")
    else:
        print("FILES PRESENT")
def call_check_if_a_file_exist_in_snipr( args):
    # parser = argparse.ArgumentParser()
    # parser.add_argument('stuff', nargs='+')
    # args = parser.parse_args()
    # print (args.stuff)
    returnvalue=0
    try:
        sessionID=args.stuff[1]
        scanID=args.stuff[2]
        resource_dir=args.stuff[3]
        URI="/data/experiments/"+sessionID+"/scans/"+scanID
        extension_to_find_list=args.stuff[4:]
        file_present=check_if_a_file_exist_in_snipr(URI, resource_dir,extension_to_find_list)
        ############
        all_files_present_flag=0
        if file_present < len(extension_to_find_list):
            subprocess.call("echo " + "I PASSED 0 AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
            return 0
        else:
            all_files_present_flag=1
        all_files_present_flag_df=pd.DataFrame([all_files_present_flag])
        all_files_present_flag_df.columns=['all_files_present_flag']
        all_files_present_flag_df.to_csv('/workinginput/all_files_present_flag_df.csv',index=False)
        returnvalue=1
        ########
        # if file_present < len(extension_to_find_list):
        #     pass
        # else:
        #     returnvalue=1
        # return 1
        subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass
    return  returnvalue

def get_latest_file_for_analytics(df_listfile): ##,SCAN_URI_NIFTI_FILEPREFIX=""):
    allfileswithprefix1_df=df_listfile
    # if len(SCAN_URI_NIFTI_FILEPREFIX)>0:
    #     allfileswithprefix1_df=allfileswithprefix1_df[allfileswithprefix1_df.URI.str.contains(SCAN_URI_NIFTI_FILEPREFIX)]
    allfileswithprefix1_df["FILE_BASENAME"]=allfileswithprefix1_df["URI"].apply(os.path.basename)

    # allfileswithprefix1_df['FILE_BASENAME']=allfileswithprefix1_df["FILENAME"].apply(os.path.basename)
    allfileswithprefix1_df['DATE']=allfileswithprefix1_df['FILE_BASENAME']
    allfileswithprefix1_df['DATE'] = allfileswithprefix1_df['DATE'].str[-18:-4]
    allfileswithprefix1_df['DATETIME'] =    allfileswithprefix1_df['DATE']
    allfileswithprefix1_df['DATETIME'] = pd.to_datetime(allfileswithprefix1_df['DATETIME'], format='%Y%m%d%H%M%S', errors='coerce')
    allfileswithprefix1_df = allfileswithprefix1_df.sort_values(by=['DATETIME'], ascending=False)
    # print(allfileswithprefix1_df["DATETIME"])
    allfileswithprefix1_df=allfileswithprefix1_df.reset_index(drop=True)
    x_df=allfileswithprefix1_df.iloc[[0]]
    return x_df

def get_latest_file(df_listfile): ##,SCAN_URI_NIFTI_FILEPREFIX=""):
    allfileswithprefix1_df=df_listfile
    # if len(SCAN_URI_NIFTI_FILEPREFIX)>0:
    #     allfileswithprefix1_df=allfileswithprefix1_df[allfileswithprefix1_df.URI.str.contains(SCAN_URI_NIFTI_FILEPREFIX)]
    allfileswithprefix1_df["FILE_BASENAME"]=allfileswithprefix1_df["URI"].apply(os.path.basename)

    # allfileswithprefix1_df['FILE_BASENAME']=allfileswithprefix1_df["FILENAME"].apply(os.path.basename)
    allfileswithprefix1_df['DATE']=allfileswithprefix1_df['FILE_BASENAME']
    allfileswithprefix1_df['DATE'] = allfileswithprefix1_df['DATE'].str[-16:-4]
    allfileswithprefix1_df['DATETIME'] =    allfileswithprefix1_df['DATE']
    allfileswithprefix1_df['DATETIME'] = pd.to_datetime(allfileswithprefix1_df['DATETIME'], format='%Y%m%d%H%M', errors='coerce')
    allfileswithprefix1_df = allfileswithprefix1_df.sort_values(by=['DATETIME'], ascending=False)
    # print(allfileswithprefix1_df["DATETIME"])
    allfileswithprefix1_df=allfileswithprefix1_df.reset_index(drop=True)
    x_df=allfileswithprefix1_df.iloc[[0]]
    return x_df

def download_a_singlefile_with_URLROW(url,dir_to_save):
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    # command="echo  " + url['URI'] + " >> " +  os.path.join(dir_to_save,"test.csv")
    # subprocess.call(command,shell=True)
    response = xnatSession.httpsess.get(xnatSession.host +url.loc[0,"URI"]) #/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv") #
    #                                                       # "/data/experiments/SNIPR02_E03548/scans/1-CT1/resources/147851/files/ICH_0001_01022017_0414_1-CT1_threshold-1024.0_22121.0TOTAL_VersionDate-11302022_04_22_2023.csv") ## url['URI'])
    zipfilename=os.path.join(dir_to_save,os.path.basename(url.loc[0,"Name"]) ) #"/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv")) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    #xnatSession.close_httpsession())
    return zipfilename
def get_latest_file_SAH(df_listfile): ##,SCAN_URI_NIFTI_FILEPREFIX=""):
    allfileswithprefix1_df=df_listfile
    # if len(SCAN_URI_NIFTI_FILEPREFIX)>0:
    #     allfileswithprefix1_df=allfileswithprefix1_df[allfileswithprefix1_df.URI.str.contains(SCAN_URI_NIFTI_FILEPREFIX)]
    allfileswithprefix1_df["FILE_BASENAME"]=allfileswithprefix1_df["URI"].apply(os.path.basename)

    # allfileswithprefix1_df['FILE_BASENAME']=allfileswithprefix1_df["FILENAME"].apply(os.path.basename)
    allfileswithprefix1_df['DATE']=allfileswithprefix1_df['FILE_BASENAME']
    allfileswithprefix1_df['DATE'] = allfileswithprefix1_df['DATE'].str[-14:-4]
    allfileswithprefix1_df['DATETIME'] =    allfileswithprefix1_df['DATE']
    allfileswithprefix1_df['DATETIME'] = pd.to_datetime(allfileswithprefix1_df['DATETIME'], format='%m_%d_%Y', errors='coerce')
    allfileswithprefix1_df = allfileswithprefix1_df.sort_values(by=['DATETIME'], ascending=False)
    # print(allfileswithprefix1_df["DATETIME"])
    allfileswithprefix1_df=allfileswithprefix1_df.reset_index(drop=True)
    x_df=allfileswithprefix1_df.iloc[[0]]
    return x_df
def get_latest_file_ICH_CSV_COLDROPPED(df_listfile): ##,SCAN_URI_NIFTI_FILEPREFIX=""):
    allfileswithprefix1_df=df_listfile
    # if len(SCAN_URI_NIFTI_FILEPREFIX)>0:
    #     allfileswithprefix1_df=allfileswithprefix1_df[allfileswithprefix1_df.URI.str.contains(SCAN_URI_NIFTI_FILEPREFIX)]
    allfileswithprefix1_df["FILE_BASENAME"]=allfileswithprefix1_df["URI"].apply(os.path.basename)

    # allfileswithprefix1_df['FILE_BASENAME']=allfileswithprefix1_df["FILENAME"].apply(os.path.basename)
    allfileswithprefix1_df['DATE']=allfileswithprefix1_df['FILE_BASENAME']
    allfileswithprefix1_df['DATE'] = allfileswithprefix1_df['DATE'].str[(-14-13):(-4-13)]
    allfileswithprefix1_df['DATETIME'] =    allfileswithprefix1_df['DATE']
    allfileswithprefix1_df['DATETIME'] = pd.to_datetime(allfileswithprefix1_df['DATETIME'], format='%m_%d_%Y', errors='coerce')
    allfileswithprefix1_df = allfileswithprefix1_df.sort_values(by=['DATETIME'], ascending=False)
    # print(allfileswithprefix1_df["DATETIME"])
    allfileswithprefix1_df=allfileswithprefix1_df.reset_index(drop=True)
    x_df=allfileswithprefix1_df.iloc[[0]]
    return x_df

def call_download_a_singlefile_with_URIString(args):
    url=args.stuff[1]
    filename=args.stuff[2]
    dir_to_save=args.stuff[3]
    download_a_singlefile_with_URIString(url,filename,dir_to_save)
    return
def delete_a_file_with_URIString(url):
    try:
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()
        response = xnatSession.httpsess.delete(xnatSession.host +url)
        subprocess.call("echo " + "I PASSED AT ::{}::RESPONSE::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3],response) ,shell=True )
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass

def download_a_singlefile_with_URIString(url,filename,dir_to_save):
    print("url::{}::filename::{}::dir_to_save::{}".format(url,filename,dir_to_save))
    # #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    # command="echo  " + url['URI'] + " >> " +  os.path.join(dir_to_save,"test.csv")
    # subprocess.call(command,shell=True)
    response = xnatSession.httpsess.get(xnatSession.host +url) #/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv") #
    #                                                       # "/data/experiments/SNIPR02_E03548/scans/1-CT1/resources/147851/files/ICH_0001_01022017_0414_1-CT1_threshold-1024.0_22121.0TOTAL_VersionDate-11302022_04_22_2023.csv") ## url['URI'])
    zipfilename=os.path.join(dir_to_save,filename ) #"/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv")) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    # #xnatSession.close_httpsession())
    return zipfilename
def download_an_xmlfile_with_URIString(args): #url,filename,dir_to_save):
    returnvalue=0

    try:
        session_ID=str(args.stuff[1])
        filename=str(args.stuff[2])
        dir_to_save=str(args.stuff[3])
        subprocess.call('echo working:' +session_ID+' > /workingoutput/testatul.txt',shell=True)
        subprocess.call('echo working:' +filename+' > /workingoutput/testatul.txt',shell=True)
        subprocess.call('echo working:' +dir_to_save+' > /workingoutput/testatul.txt',shell=True)
        print("url::{}::filename::{}::dir_to_save::{}".format(session_ID,filename,dir_to_save))
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()

        # command="echo  " + url['URI'] + " >> " +  os.path.join(dir_to_save,"test.csv")
        # subprocess.call(command,shell=True) https://snipr.wustl.edu/app/action/XDATActionRouter/xdataction/xml/search_element/xnat%3ActSessionData/search_field/xnat%3ActSessionData.ID/search_value/SNIPR01_E07665
        # https://snipr.wustl.edu/app/action/XDATActionRouter/xdataction/xml_file/search_element/xnat%3ActSessionData/search_field/xnat%3ActSessionData.ID/search_value/SNIPR02_E03847
        url='/app/action/XDATActionRouter/xdataction/xml_file/search_element/xnat%3ActSessionData/search_field/xnat%3ActSessionData.ID/search_value/'+str(session_ID)  ##+'/popup/false/project/ICH'
        subprocess.call("echo " + "I url AT ::{}  >> /workingoutput/error.txt".format(xnatSession.host +url) ,shell=True )
        xmlfilename=os.path.join(dir_to_save,filename )
        try:
            response = xnatSession.httpsess.get(xnatSession.host +url) #/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv") #
            num_files_present=0
            subprocess.call("echo " + "I response AT ::{}  >> /workingoutput/error.txt".format(response) ,shell=True )
            metadata_masks=response.text #json()['ResultSet']['Result']
            f = open(xmlfilename, "w")
            f.write(metadata_masks)
            f.close()
            # if response.status_code != 200:
        except:
            command='curl -u '+ XNAT_USER +':'+XNAT_PASS+' -X GET '+ xnatSession.host +url + ' > '+ xmlfilename
            subprocess.call(command,shell=True)
            subprocess.call("echo " + "I LINE 2096 AT ::{}::{}  >> /workingoutput/error.txt".format(xmlfilename,inspect.stack()[0][3]) ,shell=True )
            print("I PASSED AT ::{}".format(inspect.stack()[0][3]))
        # #xnatSession.close_httpsession())
            # return num_files_present



        # zipfilename=os.path.join(dir_to_save,filename ) #"/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv")) #sessionId+scanId+'.zip'
        # with open(zipfilename, "wb") as f:
        #     for chunk in response.iter_content(chunk_size=512):
        #         if chunk:  # filter out keep-alive new chunks
        #             f.write(chunk)
        #xnatSession.close_httpsession())
        returnvalue=1
        subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        print("I PASSED AT ::{}".format(inspect.stack()[0][3]))
    except:

        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
    return returnvalue

def download_an_xmlfile_with_URIString_func(session_ID,filename,dir_to_save): #url,filename,dir_to_save):
    returnvalue=0

    try:
        # session_ID=str(args.stuff[1])
        # filename=str(args.stuff[2])
        # dir_to_save=str(args.stuff[3])
        subprocess.call('echo working:' +session_ID+' > /workingoutput/testatul.txt',shell=True)
        subprocess.call('echo working:' +filename+' > /workingoutput/testatul.txt',shell=True)
        subprocess.call('echo working:' +dir_to_save+' > /workingoutput/testatul.txt',shell=True)
        print("url::{}::filename::{}::dir_to_save::{}".format(session_ID,filename,dir_to_save))
        #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        #xnatSession.renew_httpsession()

        # command="echo  " + url['URI'] + " >> " +  os.path.join(dir_to_save,"test.csv")
        # subprocess.call(command,shell=True)
        # https://snipr.wustl.edu/app/action/XDATActionRouter/xdataction/xml_file/search_element/xnat%3ActSessionData/search_field/xnat%3ActSessionData.ID/search_value/SNIPR02_E03847
        url='/app/action/XDATActionRouter/xdataction/xml_file/search_element/xnat%3ActSessionData/search_field/xnat%3ActSessionData.ID/search_value/'+str(session_ID)  ##+'/popup/false/project/ICH'
        subprocess.call("echo " + "I url AT ::{}  >> /workingoutput/error.txt".format(xnatSession.host +url) ,shell=True )
        xmlfilename=os.path.join(dir_to_save,filename )
        try:
            response = xnatSession.httpsess.get(xnatSession.host +url) #/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv") #
            num_files_present=0
            subprocess.call("echo " + "I response AT ::{}  >> /workingoutput/error.txt".format(response) ,shell=True )
            metadata_masks=response.text #json()['ResultSet']['Result']
            f = open(xmlfilename, "w")
            f.write(metadata_masks)
            f.close()
            # if response.status_code != 200:
        except:
            command='curl -u '+ XNAT_USER +':'+XNAT_PASS+' -X GET '+ xnatSession.host +url + ' > '+ xmlfilename
            subprocess.call(command,shell=True)
        # #xnatSession.close_httpsession())
        # return num_files_present



        # zipfilename=os.path.join(dir_to_save,filename ) #"/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv")) #sessionId+scanId+'.zip'
        # with open(zipfilename, "wb") as f:
        #     for chunk in response.iter_content(chunk_size=512):
        #         if chunk:  # filter out keep-alive new chunks
        #             f.write(chunk)
        #xnatSession.close_httpsession())
        returnvalue=1
        subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        print("I PASSED AT ::{}".format(inspect.stack()[0][3]))
    except:

        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        print("I PASSED AT ::{}".format(inspect.stack()[0][3]))
    return returnvalue


def listoffile_witha_URI_as_df(URI):
    # #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()
    # print("I AM IN :: listoffile_witha_URI_as_df::URI::{}".format(URI))

    response = xnatSession.httpsess.get(xnatSession.host + URI)
    # print("I AM IN :: listoffile_witha_URI_as_df::URI::{}".format(URI))
    num_files_present=0
    df_scan=[]
    if response.status_code != 200:
        # #xnatSession.close_httpsession())
        return num_files_present
    # subprocess.call("echo " + "I PASSED ATUL  ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
    metadata_masks=response.json()['ResultSet']['Result']
    df_listfile = pd.read_json(json.dumps(metadata_masks))
    # #xnatSession.close_httpsession())
    return df_listfile
def download_files_in_a_resource(URI,dir_to_save):
    try:
        df_listfile=listoffile_witha_URI_as_df(URI)
        print("df_listfile::{}".format(df_listfile))
        # download_a_singlefile_with_URLROW(df_listfile,dir_to_save)
        for item_id, row in df_listfile.iterrows():
            # print("row::{}".format(row))
            # download_a_singlefile_with_URLROW(row,dir_to_save)
            download_a_singlefile_with_URIString(row['URI'],row['Name'],dir_to_save)
            print("DOWNLOADED ::{}".format(row))
    except:
        print("FAILED AT ::{}".format("download_files_in_a_resource"))
        pass
def download_files_in_scans_resources_withname_sh():
    sessionId=sys.argv[1]
    scan_id=sys.argv[2]
    resource_dirname=sys.argv[3]
    dir_to_save=sys.argv[4]
    try:
        URI = (("/data/experiments/%s")  %
               (sessionId))
        session_meta_data=get_metadata_session(URI)
        session_meta_data_df = pd.read_json(json.dumps(session_meta_data))
        for index, row in session_meta_data_df.iterrows():

            URI = ((row["URI"]+"/resources/" + resource_dirname+ "/files?format=json")  %
               (sessionId))
            df_listfile=listoffile_witha_URI_as_df(URI)
            print("df_listfile::{}".format(df_listfile))
        # download_a_singlefile_with_URLROW(df_listfile,dir_to_save)
            for item_id, row in df_listfile.iterrows():
                if str(row["ID"])==str(scan_id):
                    # print("row::{}".format(row))
                    # download_a_singlefile_with_URLROW(row,dir_to_save)
                    download_a_singlefile_with_URIString(row['URI'],row['Name'],dir_to_save)
                    print("DOWNLOADED ::{}".format(row))
                    print("PASSED AT ::{}".format("download_files_in_a_resource"))

    except:
        print("FAILED AT ::{}".format("download_files_in_a_resource"))
        pass

   
def download_files_in_a_resource_withname(sessionId,resource_dirname,dir_to_save):
    try:
        URI = (("/data/experiments/%s/resources/" + resource_dirname+ "/files?format=json")  %
               (sessionId))
        df_listfile=listoffile_witha_URI_as_df(URI)
        print("df_listfile::{}".format(df_listfile))
        # download_a_singlefile_with_URLROW(df_listfile,dir_to_save)
        for item_id, row in df_listfile.iterrows():
            # print("row::{}".format(row))
            # download_a_singlefile_with_URLROW(row,dir_to_save)
            download_a_singlefile_with_URIString(row['URI'],row['Name'],dir_to_save)
            print("DOWNLOADED ::{}".format(row))
    except:
        print("FAILED AT ::{}".format("download_files_in_a_resource"))
        pass
def call_download_files_in_a_resource_in_a_session(args):
    returnvalue=0
    sessionId=args.stuff[1]
    # scanId=args.stuff[2]

    resource_dirname=args.stuff[2]
    dir_to_save=args.stuff[3]
    URI = (("/data/experiments/%s/resources/" + resource_dirname+ "/files?format=json")  %
        (sessionId))
    # Log failure message for debugging
    command = f"echo passed at call_download_files_in_a_resource_in_a_session: {inspect.stack()[0][3]} >> /output/error.txt"
    subprocess.call(command, shell=True)
    try:
        download_files_in_a_resource(URI,dir_to_save)
        print("I AM IN :: call_download_files_in_a_resource_in_a_session::URI::{}".format(URI))
        return 1
    except:
        pass
    return returnvalue
    # URI,dir_to_save
def call_concatenate_csv_list(args):
    all_files=args.stuff[2:]
    outputfilename=args.stuff[1]
    df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
    df=df.drop_duplicates()
    df.to_csv(outputfilename,index=False)

def download_all_csv_files_givena_URIdf(URI_DF,projectname,dir_to_save):
    try:
        URI_DF_WITH_CSVFILES=URI_DF[URI_DF[projectname+'_CSVFILE_AVAILABLE']==1]
        print("URI_DF_WITH_CSVFILESshape::{}".format(URI_DF_WITH_CSVFILES.shape))
        for item_id1, each_selected_scan in URI_DF_WITH_CSVFILES.iterrows():
            download_a_singlefile_with_URIString(each_selected_scan[projectname+'_CSVFILENAME'],os.path.basename(each_selected_scan[projectname+'_CSVFILENAME']),dir_to_save)
        print("I SUCCEEDED AT ::{}".format(inspect.stack()[0][3]))
            # pass
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
    return
def download_files_with_mastersessionlist(sessionlist_filename,masktype,filetype,dir_to_save,listofsession_current=""):
    try:
        if os.path.exists(listofsession_current):
            listofsession_current_df=pd.read_csv(listofsession_current)

        sessionlist_filename_df=pd.read_csv(sessionlist_filename)
        sessionlist_filename_df=sessionlist_filename_df[sessionlist_filename_df[masktype+'_'+filetype+'FILE_AVAILABLE']==1]
        # print("URI_DF_WITH_CSVFILESshape::{}".format(sessionlist_filename_df))
        files_local_location=[]
        for item_id1, each_selected_scan in sessionlist_filename_df.iterrows():
            # print("CSV FILE URL::{}".format(each_selected_scan[masktype+'_'+filetype+'FILENAME']))
            this_filename=os.path.join(dir_to_save,os.path.basename(each_selected_scan[masktype+'_'+filetype+'FILENAME']))
            download_a_singlefile_with_URIString(each_selected_scan[masktype+'_'+filetype+'FILENAME'],os.path.basename(each_selected_scan[masktype+'_'+filetype+'FILENAME']),dir_to_save)
            if ".csv" in this_filename:
                this_filename_df=pd.read_csv(this_filename)
                this_filename_df['SESSION_ID']=each_selected_scan[masktype+'_'+filetype+'FILENAME'].split('/')[3]
                this_filename_df['SESSION_LABEL']=each_selected_scan['label'] ##.split('/')[3]
                this_filename_df['SCAN_ID']=each_selected_scan[masktype+'_'+filetype+'FILENAME'].split('/')[5]
                this_filename_df['SCAN_TYPE']=each_selected_scan['SCAN_TYPE']
                # this_filename_df['FILEPATH'+filetype]=each_selected_scan[masktype+'_'+filetype+'FILENAME'] #.split('/')[3]
            # listofsession_current_df_row=listofsession_current_df[listofsession_current_df['SESSION_ID']==each_selected_scan[masktype+'_'+filetype+'FILENAME'].split('/')[3]]
            # print("listofsession_current exists::{}".format(listofsession_current_df_row  ))
                this_filename_df.to_csv(this_filename,index=False)
            files_local_location.append(this_filename)
        print("I SUCCEEDED AT ::{}".format(inspect.stack()[0][3]))
        return files_local_location

            # pass
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
    return
def call_download_files_with_mastersessionlist(args):
    try:
        sessionlist_filename=args.stuff[1]
        masktype=args.stuff[2]
        filetype=args.stuff[3]
        dir_to_save=args.stuff[4]
        localfilelist_csv=args.stuff[5]
        listofsession_current=args.stuff[6]
        files_local_location=download_files_with_mastersessionlist(sessionlist_filename,masktype,filetype,dir_to_save,listofsession_current=listofsession_current)
        files_local_location_df=pd.DataFrame(files_local_location)
        files_local_location_df.columns=['LOCAL_FILENAME']
        files_local_location_df.to_csv(localfilelist_csv,index=False)
        # if upload_flag==1:
        #     projectId=args.stuff[6]
        #     resource_dirname=args.stuff[7]
        #     for each_file in files_local_location:
        #         uploadsinglefile_X_level('projects',projectId,each_file,resource_dirname)

        print("I SUCCEEDED AT ::{}".format(inspect.stack()[0][3]))
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
        return 0
def call_download_all_csv_files_givena_URIdf(args):
    try:
        URI_DF=pd.read_csv(args.stuff[1])
        # scanID=args.stuff[2]
        dir_to_save=args.stuff[2]
        projectname=args.stuff[3]
        print("URI_DF::{}::projectname::{}::dir_to_save::{}".format(URI_DF.shape,projectname,dir_to_save))
        download_all_csv_files_givena_URIdf(URI_DF,projectname,dir_to_save)
        print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
def divide_sessionlist_done_vs_undone(sessionlist_file,masktype):
    try:
        print("THIS FILENAME IS : {}".format(sessionlist_file))
        sessionlist_file_df=pd.read_csv(sessionlist_file)
        sessionlist_file_df_done=sessionlist_file_df[sessionlist_file_df[masktype+'_PDFFILE_AVAILABLE']==1]
        sessionlist_file_df_notdone=sessionlist_file_df[sessionlist_file_df[masktype+'_PDFFILE_AVAILABLE']!=1]
        sessionlist_file_df_done.to_csv(sessionlist_file.split('.csv')[0]+'_done.csv' ,index=False)
        sessionlist_file_df_notdone.to_csv(sessionlist_file.split('.csv')[0]+'_not_done.csv' ,index=False)
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
        return 0
def call_divide_sessionlist_done_vs_undone(args):
    try:
        sessionlist_file=args.stuff[1]
        masktype=args.stuff[2]
        divide_sessionlist_done_vs_undone(sessionlist_file,masktype)
        print("I SUCCEED AT ::{}".format(inspect.stack()[0][3]))
        return 1
    except:
        print("I FAILED AT ::{}".format(inspect.stack()[0][3]))
        pass
        return 0
def project_resource_latest_analytic_file(args):
    try:
        print("WO ZAI call_project_resource_latest_analytic_file try")
        projectID=args.stuff[1]
        # scanID=args.stuff[2]
        resource_dir=args.stuff[2]
        URI="/data/projects/"+projectID #+"/scans/"+scanID
        URI = (URI+'/resources/' + resource_dir +'/files?format=json')
        extension_to_find_list=args.stuff[3]
        dir_to_save=args.stuff[4]
        print("projectID::{}::resource_dir::{}::URI::{}::extension_to_find_list::{}::dir_to_save::{}".format(projectID,resource_dir,URI,extension_to_find_list,dir_to_save))
        df_listfile=listoffile_witha_URI_as_df(URI)
        df_listfile=df_listfile[df_listfile.URI.str.contains(extension_to_find_list)]
        latest_filename=get_latest_file(df_listfile)
        print(latest_filename['URI'])
        print("\n")
        print(dir_to_save)
        print("\n")
        print("WO ZAI ::{}".format("call_project_resource_latest_analytic_file"))

        filename_saved=download_a_singlefile_with_URLROW(latest_filename,dir_to_save)
        # # if len(filename_saved) >0 :
        # filename_saved_df=pd.read_csv(filename_saved)
        # required_col = filename_saved_df.columns[filename_saved_df.columns.str.contains(pat = 'PDFFILE_AVAILABLE')]
        # print("required_col:{}".format(required_col[0]))
        # filename_saved_df_notdone=filename_saved_df[filename_saved_df[required_col[0]]!=1]
        # filename_saved_df_done=filename_saved_df[filename_saved_df[required_col[0]]==1]
        # filename_notdone=os.path.join(dir_to_save,"sessions.csv")
        # filename_done=os.path.join(dir_to_save,"sessions_done.csv")
        # filename_saved_df_notdone.to_csv(filename_notdone,index=False)
        # filename_saved_df_done.to_csv(filename_done,index=False)
        return "CSVMASTERFILE::"+filename_saved
    except:
        return 0
    #
    # file_present=check_if_a_file_exist_in_snipr(URI, resource_dir,extension_to_find_list)
    # if file_present < len(extension_to_find_list):
    #     return
# def get_file_for_second_round():
def get_selected_scan_info(SESSION_ID, dir_to_save):
    # Log failure message for debugging
    command = f"echo passed at each_row_id: {inspect.stack()[0][3]} >> /output/error.txt"
    subprocess.call(command, shell=True)

    # Define the URI and URL for the request
    URI = f'/data/experiments/{SESSION_ID}'
    url = f"{URI}/resources/NIFTI_LOCATION/files?format=json"

    # Initialize XNAT session
    #xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    #xnatSession.renew_httpsession()

    try:
        # Make a GET request to the XNAT server
        response = xnatSession.httpsess.get(xnatSession.host + url)
        response.raise_for_status()  # Raise an error for unsuccessful responses
        metadata_masks = response.json()['ResultSet']['Result']

        # Convert metadata to a DataFrame
        df_scan = pd.read_json(json.dumps(metadata_masks))

        # Log additional debug information
        command = f"echo passed at each_row_id: {df_scan['URI'].iloc[0]} >> /output/error.txt"
        subprocess.call(command, shell=True)

        # Download the file specified by the URI
        download_a_singlefile_with_URIString(
            str(df_scan['URI'].iloc[0]),
            os.path.basename(str(df_scan['URI'].iloc[0])),
            dir_to_save
        )

        # Read the downloaded file to extract SCAN_ID and SCAN_NAME
        nifti_location = pd.read_csv(
            os.path.join(dir_to_save, os.path.basename(str(df_scan['URI'].iloc[0])))
        )
        SCAN_ID = str(nifti_location.loc[nifti_location.index[0], 'ID'])
        SCAN_NAME = str(nifti_location.loc[nifti_location.index[0], 'Name'])

        # Log success message
        command = f"echo passed at each_row_id: {inspect.stack()[0][3]} >> /output/error.txt"
        subprocess.call(command, shell=True  )

        return SCAN_ID, SCAN_NAME

    except Exception as e:
        # Log exception details for debugging
        command = f"echo exception at {inspect.stack()[0][3]}: {str(e)} >> /output/error.txt"
        subprocess.call(command, shell=True)
        raise e

    finally:
        print('Hello world')
        # Close the XNAT session
        #xnatSession.close_httpsession())

def call_download_a_file_with_ext(args):
    command = f"echo exception at {inspect.stack()[0][3]}: WO ZAI ZELI >> /output/error.txt"
    subprocess.call(command, shell=True)
    session_id=args.stuff[1]
    scan_id=args.stuff[2]
    resource_dir=args.stuff[3]
    extensions_to_download=args.stuff[4]
    outputfolder=args.stuff[5]
    prefix_if_any = ''
    if len(args.stuff)>6: ##.stuff[6]:
        prefix_if_any=args.stuff[6]
    try:
        download_a_file_with_ext(session_id, scan_id, resource_dir, extensions_to_download, outputfolder, prefix_if_any=prefix_if_any)
    except Exception as e:
        command = f"echo exception at {inspect.stack()[0][3]}: {str(e)} >> /output/error.txt"
        subprocess.call(command, shell=True)
    return 1

def download_a_file_with_ext(session_id,scan_id,resource_dir,extensions_to_download,outputfolder,prefix_if_any=''):
    #         resource_dir='MASKS' #'NIFTI_LOCATION'
    try:

        URL='/data/experiments/'+session_id+'/scans/'+scan_id
        metadata_masks=get_resourcefiles_metadata(URL,resource_dir)
        df_scan = pd.read_json(json.dumps(metadata_masks))
        #         extensions_to_delete=['_resaved_levelset_sulci_above_ventricle.nii.gz','_resaved_levelset_sulci_at_ventricle.nii.gz','_resaved_levelset_sulci_below_ventricle.nii.gz',
        #                                  '_resaved_levelset_sulci_total.nii.gz','_resaved_levelset_ventricle_total.nii.gz']
        # for each_extension in extensions_to_delete:
        matched_rows = df_scan[df_scan['URI'].str.contains(extensions_to_download, case=False, na=False)]
        command = "echo  success at  download: " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        if len(prefix_if_any)>0:
            matched_rows = matched_rows[matched_rows['URI'].str.contains(prefix_if_any, case=False, na=False)]

        if matched_rows.shape[0]>0:
            matched_rows=matched_rows.reset_index()
            print(matched_rows)
            for each_row_id,each_row in matched_rows.iterrows():
                command = "echo  success at  download each_row_id: " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
                subprocess.call(command,shell=True)
                url=each_row['URI'] #matched_rows.at[0,'URI']
                print(url)
                download_a_singlefile_with_URIString(url,os.path.basename(url),outputfolder)
                # print("DELETED::{}".format(url))

    except:
        pass


def delete_file_with_ext(session_id,scan_id,resource_dir,extensions_to_delete,prefix_if_any=''):
    #         resource_dir='MASKS' #'NIFTI_LOCATION'
    try:

        URL='/data/experiments/'+session_id+'/scans/'+scan_id
        metadata_masks=get_resourcefiles_metadata(URL,resource_dir)
        df_scan = pd.read_json(json.dumps(metadata_masks))
        #         extensions_to_delete=['_resaved_levelset_sulci_above_ventricle.nii.gz','_resaved_levelset_sulci_at_ventricle.nii.gz','_resaved_levelset_sulci_below_ventricle.nii.gz',
        #                                  '_resaved_levelset_sulci_total.nii.gz','_resaved_levelset_ventricle_total.nii.gz']
        # for each_extension in extensions_to_delete:
        matched_rows = df_scan[df_scan['URI'].str.contains(extensions_to_delete, case=False, na=False)]
        command = "echo  success at  DELETED: " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        if len(prefix_if_any)>0:
            matched_rows = matched_rows[matched_rows['URI'].str.contains(prefix_if_any, case=False, na=False)]

        if matched_rows.shape[0]>0:
            matched_rows=matched_rows.reset_index()
            print(matched_rows)
            for each_row_id,each_row in matched_rows.iterrows():
                command = "echo  success at  DELETED each_row_id: " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
                subprocess.call(command,shell=True)
                url=each_row['URI'] #matched_rows.at[0,'URI']
                print(url)
                delete_a_file_with_URIString(url)
                print("DELETED::{}".format(url))

    except:
        pass

def call_delete_file_with_ext(args): #session_id,scan_id,resource_dir,extensions_to_delete):
    try:
        session_id=args.stuff[1]
        scan_id=args.stuff[2]
        resource_dir=args.stuff[3]
        extensions_to_delete=args.stuff[4]
        prefix_if_any=''
        if len(args.stuff)>5:

            prefix_if_any=args.stuff[5]
        delete_file_with_ext(session_id,scan_id,resource_dir,extensions_to_delete,prefix_if_any=prefix_if_any)
        command = "echo  success at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        return 1
    except:
        command = "echo  failed at : " +  inspect.stack()[0][3]  + " >> " + "/output/error.txt"
        subprocess.call(command,shell=True)
        pass
        return 0

def find_selected_scan_id(session_id):
    """
    Return (scan_id, scan_name) for the scan previously selected for analysis.

    This reads the CSV saved under the XNAT session's NIFTI_LOCATION resource
    (created by your decision_which_nifti/select_scan_for_analysis step).
    Raises ValueError if not found.
    """
    import json, io
    import pandas as pd

    # 1) List files under NIFTI_LOCATION for this session
    base_uri = f"/data/experiments/{session_id}"
    list_url = f"{base_uri}/resources/NIFTI_LOCATION/files?format=json"

    resp = xnatSession.httpsess.get(xnatSession.host + list_url)
    resp.raise_for_status()
    results = resp.json().get("ResultSet", {}).get("Result", [])

    if not results:
        raise ValueError(f"No NIFTI_LOCATION files found for session {session_id}.")

    # If multiple CSVs exist, prefer the most recently created one (if field present)
    df_list = pd.read_json(json.dumps(results))
    if "created" in df_list.columns:
        df_list = df_list.sort_values("created", ascending=False)

    file_uri = df_list["URI"].iloc[0]

    # 2) Download the selected NIFTI_LOCATION CSV (without writing to disk)
    file_resp = xnatSession.httpsess.get(xnatSession.host + file_uri)
    file_resp.raise_for_status()

    nifti_loc_df = pd.read_csv(io.StringIO(file_resp.text))

    # Expect columns: 'ID' (scan id), 'Name' (nifti filename), etc.
    if nifti_loc_df.empty or "ID" not in nifti_loc_df.columns or "Name" not in nifti_loc_df.columns:
        raise ValueError(f"NIFTI_LOCATION file for {session_id} is missing expected columns.")

    scan_id  = str(nifti_loc_df.iloc[0]["ID"])
    scan_name = str(nifti_loc_df.iloc[0]["Name"])
    result = f'"SCAN_ID"::{scan_id}::"SCAN_NAME"::{scan_name}'
    print(result)
    return scan_id, scan_name ##result ##"SCAN_ID"::{scan_id)::"SCAN_NAME"::{scan_name}

def get_largest_newest_csv_for_scan(session_id, scan_id, resource_label="ICH_PHE_QUANTIFICATION"):
    """
    From the given scan's resource, pick the CSV that is:
      1) Largest by size (bytes), and
      2) If there’s a tie, the newest by timestamp (created/modified).
    Returns a dict: {"name": ..., "uri": ..., "size": int, "created": pandas.Timestamp}
    Raises ValueError if none found.
    """
    import json
    import pandas as pd

    # List files in the scan resource
    base = f"/data/experiments/{session_id}/scans/{scan_id}"
    list_url = f"{base}/resources/{resource_label}/files?format=json"

    r = xnatSession.httpsess.get(xnatSession.host + list_url)
    r.raise_for_status()
    rows = r.json().get("ResultSet", {}).get("Result", [])
    if not rows:
        raise ValueError(f"No files in resource '{resource_label}' for scan {scan_id} (session {session_id}).")

    df = pd.DataFrame(rows)

    # Normalize helpful columns (size + timestamp may vary by XNAT version)
    # Try common variations for size
    size_cols = [c for c in df.columns if c.lower() in {"size","filesize","file_size","file_size_bytes"}]
    if size_cols:
        size_col = size_cols[0]
    else:
        # Fallback: try to infer from 'URI' (not ideal). If missing, set 0.
        size_col = "_size_fallback"
        df[size_col] = 0

    # Try common variations for created/modified timestamp
    time_cols = [c for c in df.columns if c.lower() in {"created","modified","last_modified","timestamp"}]
    time_col = time_cols[0] if time_cols else None
    if time_col:
        df["_created_ts"] = pd.to_datetime(df[time_col], errors="coerce")
    else:
        df["_created_ts"] = pd.NaT

    # Prefer extension by Name; fall back to URI
    name_col = "Name" if "Name" in df.columns else ("name" if "name" in df.columns else None)
    uri_col  = "URI"  if "URI"  in df.columns else ("uri"  if "uri"  in df.columns else None)
    if not uri_col:
        raise ValueError("File listing is missing 'URI' field; cannot proceed.")

    def is_csv(row):
        name = (row[name_col] if name_col else None) or ""
        uri  = row[uri_col] or ""
        return str(name).lower().endswith(".csv") or str(uri).lower().endswith(".csv")

    csv_df = df[df.apply(is_csv, axis=1)].copy()
    if csv_df.empty:
        raise ValueError(f"No CSV files found in resource '{resource_label}' for scan {scan_id}.")

    # Ensure numeric size, missing -> 0
    csv_df["_size_bytes"] = pd.to_numeric(csv_df[size_col], errors="coerce").fillna(0).astype(int)

    # Sort: largest size first, then newest timestamp
    csv_df = csv_df.sort_values(by=["_size_bytes","_created_ts"], ascending=[False, False])

    top = csv_df.iloc[0]
    return {
        "name": top[name_col] if name_col else top[uri_col].split("/")[-1],
        "uri":  top[uri_col],
        "size": int(top["_size_bytes"]),
        "created": top["_created_ts"],
    }
def get_largest_newest_pdf_for_scan(session_id, scan_id, resource_label="ICH_PHE_QUANTIFICATION"):
    """
    From the given scan's resource, pick the PDF that is:
      1) Largest by size (bytes), and
      2) If there’s a tie, the newest by timestamp (created/modified).

    Returns a dict: {"name": ..., "uri": ..., "size": int, "created": pandas.Timestamp}
    Raises ValueError if none found.
    """
    import pandas as pd

    # List files in the scan resource
    base = f"/data/experiments/{session_id}/scans/{scan_id}"
    list_url = f"{base}/resources/{resource_label}/files?format=json"

    r = xnatSession.httpsess.get(xnatSession.host + list_url)
    r.raise_for_status()
    rows = r.json().get("ResultSet", {}).get("Result", [])
    if not rows:
        raise ValueError(f"No files in resource '{resource_label}' for scan {scan_id} (session {session_id}).")

    df = pd.DataFrame(rows)

    # ---- Normalize columns (size + timestamp may vary by XNAT version)
    size_cols = [c for c in df.columns if c.lower() in {"size","filesize","file_size","file_size_bytes"}]
    size_col = size_cols[0] if size_cols else "_size_fallback"
    if size_col == "_size_fallback":
        df[size_col] = 0

    time_cols = [c for c in df.columns if c.lower() in {"created","modified","last_modified","timestamp"}]
    time_col = time_cols[0] if time_cols else None
    df["_created_ts"] = pd.to_datetime(df[time_col], errors="coerce") if time_col else pd.NaT

    name_col = "Name" if "Name" in df.columns else ("name" if "name" in df.columns else None)
    uri_col  = "URI"  if "URI"  in df.columns else ("uri"  if "uri"  in df.columns else None)
    if not uri_col:
        raise ValueError("File listing is missing 'URI' field; cannot proceed.")

    # ---- Keep only PDFs
    def is_pdf(row):
        name = (row[name_col] if name_col else "") or ""
        uri  = row[uri_col] or ""
        return str(name).lower().endswith(".pdf") or str(uri).lower().endswith(".pdf")

    pdf_df = df[df.apply(is_pdf, axis=1)].copy()
    if pdf_df.empty:
        raise ValueError(f"No PDF files found in resource '{resource_label}' for scan {scan_id}.")

    # Ensure numeric size, missing -> 0
    pdf_df["_size_bytes"] = pd.to_numeric(pdf_df[size_col], errors="coerce").fillna(0).astype(int)

    # Sort: largest first, then newest
    pdf_df = pdf_df.sort_values(by=["_size_bytes","_created_ts"], ascending=[False, False])

    top = pdf_df.iloc[0]
    return {
        "name": top[name_col] if name_col else top[uri_col].split("/")[-1],
        "uri":  top[uri_col],
        "size": int(top["_size_bytes"]),
        "created": top["_created_ts"],
    }


def download_xnat_file_to_path(file_uri, out_path):
    resp = xnatSession.httpsess.get(xnatSession.host + file_uri, stream=True)
    resp.raise_for_status()
    with open(os.path.join(out_path,os.path.basename(file_uri)), "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 16):
            if chunk:
                f.write(chunk)
    return out_path

def get_session_id_from_label(session_label):
    """
    Given a session label (human-readable name), return its XNAT session ID.

    Example:
        Input : "IBIO_0066_10182020_1848_3"
        Output: "SNIPR02_E10245"

    It queries the XNAT REST API: /data/experiments?format=json&label=<session_label>
    """
    import json

    base_url = f"/data/experiments?format=json&label={session_label}"
    url = xnatSession.host + base_url

    # Ensure XNAT session is valid
    xnatSession.renew_httpsession()

    resp = xnatSession.httpsess.get(url)
    resp.raise_for_status()

    resultset = resp.json().get("ResultSet", {}).get("Result", [])
    if not resultset:
        raise ValueError(f"No session found for label: {session_label}")

    # usually, each session_label is unique, so take the first
    session_id = resultset[0].get("ID")
    if not session_id:
        raise ValueError(f"Could not find ID field for label: {session_label}")

    return session_id

def get_first_ct_session_for_subject(project_id,subject_id):
    """
    Given an XNAT subject ID, return the earliest CT session
    as (session_id, session_label, session_date)
    """
    import re, pandas as pd
    from datetime import datetime
    xnatSession.renew_httpsession()

    url = f"{xnatSession.host}/data/projects/{project_id}/subjects/{subject_id}/experiments?format=json"
    r = xnatSession.httpsess.get(url)
    r.raise_for_status()
    rows = r.json().get("ResultSet", {}).get("Result", [])
    if not rows:
        raise ValueError(f"No experiments found for subject: {subject_id}")

    df = pd.DataFrame(rows)
    col_id = "ID"
    col_label = "label" if "label" in df.columns else "Label"
    col_xsitype = "xsiType" if "xsiType" in df.columns else None
    col_date = "date" if "date" in df.columns else None

    if col_xsitype:
        ct_df = df[df[col_xsitype].str.contains("ctsession", case=False, na=False)]
    else:
        ct_df = df[df[col_label].str.contains("_CT_", na=False)]

    if ct_df.empty:
        raise ValueError(f"No CT sessions found for subject: {subject_id}")

    def parse_date(label, date_field):
        if pd.notna(date_field) and str(date_field).strip():
            try:
                return pd.to_datetime(date_field).date()
            except Exception:
                pass
        m = re.search(r"(\d{8})", label)
        return datetime.strptime(m.group(1), "%Y%m%d").date() if m else pd.NaT

    ct_df["_parsed_date"] = [
        parse_date(row[col_label], row.get(col_date)) for _, row in ct_df.iterrows()
    ]
    ct_df = ct_df.sort_values("_parsed_date", ascending=True)
    first = ct_df.iloc[0]

    session_id = str(first[col_id]).strip()
    session_label = str(first[col_label]).strip()
    session_date = str(first["_parsed_date"])
    print(f'"SESSION_ID"::{session_id}::"LABEL"::{session_label}::"DATE"::{session_date}')
    return session_id, session_label, session_date
def get_project_storage_size(project_id):
    """
    Compute the total size of all files under a given project in XNAT.

    Returns 0 GB if the project or resources are missing or inaccessible.
    """
    import pandas as pd
    try:
        xnatSession.renew_httpsession()
        url = f"{xnatSession.host}/data/projects/{project_id}/resources?format=json"
        r = xnatSession.httpsess.get(url)
        if r.status_code != 200:
            print(f"[WARN] Unable to access project {project_id} (status {r.status_code})")
            return {"project_id": project_id, "size_bytes": 0, "size_gb": 0}

        results = r.json().get("ResultSet", {}).get("Result", [])
        if not results:
            print(f"[INFO] No resources found for project {project_id}")
            return {"project_id": project_id, "size_bytes": 0, "size_gb": 0}

        df = pd.DataFrame(results)
        size_cols = [c for c in df.columns if c.lower() in {"size", "filesize", "file_size"}]
        if not size_cols:
            print(f"[WARN] No size field found for project {project_id}")
            return {"project_id": project_id, "size_bytes": 0, "size_gb": 0}

        total_bytes = pd.to_numeric(df[size_cols[0]], errors="coerce").fillna(0).sum()
        total_gb = total_bytes / (1024 ** 3)

        print(f"[INFO] Project {project_id} total size: {total_gb:.2f} GB")
        return {"project_id": project_id, "size_bytes": int(total_bytes), "size_gb": round(total_gb, 2)}

    except Exception as e:
        print(f"[WARN] get_project_storage_size failed for {project_id}: {e}")
        return {"project_id": project_id, "size_bytes": 0, "size_gb": 0}

def batch_cleanup_from_experiment_csv(csv_path, report_csv="cleanup_report.csv", folder_name="EDEMA_BIOMARKER"):
    """
    Safely iterate through all session IDs in experiment CSV.
    For each session:
      - Checks the specified folder (e.g., 'EDEMA_BIOMARKER') for PDF > 1 MB.
      - Deletes 'PREPROCESS_SEGM' if such a PDF exists.
    Continues even if a session or folder is missing.

    Parameters
    ----------
    csv_path : str
        Path to the experiment CSV file (must contain 'ID' column).
    report_csv : str, optional
        Output path for the cleanup report CSV (default: 'cleanup_report.csv').
    folder_name : str, optional
        The resource folder name to check for PDFs (default: 'EDEMA_BIOMARKER').
    """
    import pandas as pd
    results = []

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[WARN] Could not read {csv_path}: {e}")
        pd.DataFrame().to_csv(report_csv, index=False)
        return pd.DataFrame()

    if "ID" not in df.columns:
        print(f"[WARN] 'ID' column missing in {csv_path}")
        pd.DataFrame().to_csv(report_csv, index=False)
        return pd.DataFrame()

    session_ids = df["ID"].dropna().astype(str).tolist()
    print(f"[INFO] Found {len(session_ids)} sessions in {csv_path}")

    for sid in session_ids:
        print(f"\n[INFO] Processing session: {sid}")
        try:
            res = cleanup_preprocess_if_edema_pdf_exists(sid, folder_name=folder_name)
            results.append(res)
            print(f"  → {res['reason']}")
        except Exception as e:
            results.append({"session_id": sid, "scan_id": None, "deleted": False, "reason": f"Exception: {e}"})
            print(f"  ⚠️ Exception while processing {sid}: {e}")

    summary_df = pd.DataFrame(results)
    summary_df.to_csv(report_csv, index=False)
    print(f"\n[INFO] Cleanup summary saved to: {report_csv}")

    return summary_df

# def batch_cleanup_from_experiment_csv(csv_path, report_csv="cleanup_report.csv"):
#     """
#     Safely iterate through all session IDs in experiment CSV.
#     Continues even if file or folder is missing.
#     """
#     import pandas as pd
#     results = []
#
#     try:
#         df = pd.read_csv(csv_path)
#     except Exception as e:
#         print(f"[WARN] Could not read {csv_path}: {e}")
#         pd.DataFrame().to_csv(report_csv, index=False)
#         return pd.DataFrame()
#
#     if "ID" not in df.columns:
#         print(f"[WARN] 'ID' column missing in {csv_path}")
#         pd.DataFrame().to_csv(report_csv, index=False)
#         return pd.DataFrame()
#
#     session_ids = df["ID"].dropna().astype(str).tolist()
#     print(f"[INFO] Found {len(session_ids)} sessions in {csv_path}")
#
#     for sid in session_ids:
#         print(f"\n[INFO] Processing session: {sid}")
#         try:
#             res = cleanup_preprocess_if_edema_pdf_exists(sid)
#             results.append(res)
#             print(f"  → {res['reason']}")
#             # break
#         except Exception as e:
#             results.append({"session_id": sid, "scan_id": None, "deleted": False, "reason": f"Exception: {e}"})
#             print(f"  ⚠️ Exception while processing {sid}: {e}")
#
#     summary_df = pd.DataFrame(results)
#     summary_df.to_csv(report_csv, index=False)
#     print(f"\n[INFO] Cleanup summary saved to: {report_csv}")
#
#     return summary_df
#

# def cleanup_preprocess_if_edema_pdf_exists(session_id):
#     """
#     For a given session_id:
#       1. Find the selected scan.
#       2. Check 'EDEMA_BIOMARKER' for PDF > 1 MB.
#       3. If found, delete 'PREPROCESS_SEGM'.
#     Always returns gracefully.
#     """
#     import pandas as pd
#     threshold_bytes = 1 * 1024 * 1024
#     result = {"session_id": session_id, "scan_id": None, "deleted": False, "reason": ""}
#
#     try:
#         xnatSession.renew_httpsession()
#         # scan_info_str = find_selected_scan_id(session_id)
#         scan_id, scan_name=find_selected_scan_id(session_id)
#         # if not scan_info_str or "SCAN_ID" not in scan_info_str:
#         #     result["reason"] = "No selected scan found"
#         #     return result
#
#         # scan_id = scan_info_str.split("::")[2].strip('" \n\t')
#         result["scan_id"] = scan_id
#
#         # List EDEMA_BIOMARKER
#         list_url = f"/data/experiments/{session_id}/scans/{scan_id}/resources/EDEMA_BIOMARKER/files?format=json"
#         r = xnatSession.httpsess.get(xnatSession.host + list_url)
#         if r.status_code != 200:
#             result["reason"] = f"EDEMA_BIOMARKER not accessible (status {r.status_code})"
#             return result
#
#         files = r.json().get("ResultSet", {}).get("Result", [])
#         if not files:
#             result["reason"] = "No files in EDEMA_BIOMARKER"
#             return result
#
#         df = pd.DataFrame(files)
#         name_col = "Name" if "Name" in df.columns else "name"
#         size_cols = [c for c in df.columns if c.lower() in {"size", "filesize", "file_size"}]
#         size_col = size_cols[0] if size_cols else None
#
#         if name_col not in df.columns:
#             result["reason"] = "Name column missing"
#             return result
#
#         pdf_df = df[df[name_col].str.lower().str.endswith(".pdf", na=False)]
#         if pdf_df.empty:
#             result["reason"] = "No PDF found"
#             return result
#
#         if size_col:
#             pdf_df["_size_bytes"] = pd.to_numeric(pdf_df[size_col], errors="coerce").fillna(0).astype(int)
#             large_pdfs = pdf_df[pdf_df["_size_bytes"] > threshold_bytes]
#         else:
#             large_pdfs = pdf_df
#
#         if large_pdfs.empty:
#             result["reason"] = "No PDF >1MB found"
#             return result
#
#         # Delete PREPROCESS_SEGM
#         del_url = f"/data/experiments/{session_id}/scans/{scan_id}/resources/PREPROCESS_SEGM"
#         del_resp = xnatSession.httpsess.delete(xnatSession.host + del_url)
#         if del_resp.status_code in (200, 202, 204):
#             result["deleted"] = True
#             result["reason"] = "PREPROCESS_SEGM deleted"
#         else:
#             result["reason"] = f"Delete failed ({del_resp.status_code})"
#
#     except Exception as e:
#         result["reason"] = f"Error: {e}"
#
#     return result

def cleanup_preprocess_if_edema_pdf_exists(session_id, folder_name="EDEMA_BIOMARKER"):
    """
    For a given session_id:
      1. Find the selected scan.
      2. Check the given folder (e.g., 'EDEMA_BIOMARKER') for any PDF > 1 MB.
      3. If found, delete 'PREPROCESS_SEGM'.
    Always returns gracefully.

    Parameters
    ----------
    session_id : str
        XNAT session ID.
    folder_name : str, optional
        Resource folder to check for PDFs (default: 'EDEMA_BIOMARKER').
    """
    import pandas as pd
    threshold_bytes = 1 * 1024 * 1024
    result = {"session_id": session_id, "scan_id": None, "deleted": False, "reason": ""}

    try:
        xnatSession.renew_httpsession()
        scan_id, scan_name = find_selected_scan_id(session_id)
        result["scan_id"] = scan_id

        # List files in the specified folder
        list_url = f"/data/experiments/{session_id}/scans/{scan_id}/resources/{folder_name}/files?format=json"
        r = xnatSession.httpsess.get(xnatSession.host + list_url)
        if r.status_code != 200:
            result["reason"] = f"{folder_name} not accessible (status {r.status_code})"
            return result

        files = r.json().get("ResultSet", {}).get("Result", [])
        if not files:
            result["reason"] = f"No files in {folder_name}"
            return result

        df = pd.DataFrame(files)
        name_col = "Name" if "Name" in df.columns else "name"
        size_cols = [c for c in df.columns if c.lower() in {"size", "filesize", "file_size"}]
        size_col = size_cols[0] if size_cols else None

        if name_col not in df.columns:
            result["reason"] = "Name column missing"
            return result

        pdf_df = df[df[name_col].str.lower().str.endswith(".pdf", na=False)]
        if pdf_df.empty:
            result["reason"] = "No PDF found"
            return result

        if size_col:
            pdf_df["_size_bytes"] = pd.to_numeric(pdf_df[size_col], errors="coerce").fillna(0).astype(int)
            large_pdfs = pdf_df[pdf_df["_size_bytes"] > threshold_bytes]
        else:
            large_pdfs = pdf_df

        if large_pdfs.empty:
            result["reason"] = "No PDF >1MB found"
            return result

        # Delete PREPROCESS_SEGM
        del_url = f"/data/experiments/{session_id}/scans/{scan_id}/resources/PREPROCESS_SEGM"
        del_resp = xnatSession.httpsess.delete(xnatSession.host + del_url)
        if del_resp.status_code in (200, 202, 204):
            result["deleted"] = True
            result["reason"] = "PREPROCESS_SEGM deleted"
        else:
            result["reason"] = f"Delete failed ({del_resp.status_code})"

    except Exception as e:
        result["reason"] = f"Error: {e}"

    return result

def export_project_experiments_to_csv(project_name, output_csv="project_experiments.csv"):
    """
    Safely exports experiment metadata to CSV.
    Continues even if project has no experiments or access is denied.
    """
    import pandas as pd
    try:
        xnatSession.renew_httpsession()
        url = f"{xnatSession.host}/data/projects/{project_name}/experiments?format=json"
        r = xnatSession.httpsess.get(url)
        if r.status_code != 200:
            print(f"[WARN] Unable to access project {project_name} (status {r.status_code})")
            pd.DataFrame().to_csv(output_csv, index=False)
            return pd.DataFrame()

        results = r.json().get("ResultSet", {}).get("Result", [])
        if not results:
            print(f"[INFO] No experiments found for project {project_name}")
            pd.DataFrame().to_csv(output_csv, index=False)
            return pd.DataFrame()

        df = pd.DataFrame(results)
        if "date" in df.columns:
            df = df.sort_values("date", ascending=True)
        df.to_csv(output_csv, index=False)
        print(f"[INFO] Exported {len(df)} experiments from project '{project_name}' to {output_csv}")
        return df

    except Exception as e:
        print(f"[WARN] export_project_experiments_to_csv failed for {project_name}: {e}")
        pd.DataFrame().to_csv(output_csv, index=False)
        return pd.DataFrame()

def upload_project_file_to_xnat(project_id, file_path, resource_name="AUDIT_REPORTS"):
    """
    Uploads a local file (e.g., audit CSV, cleanup report, etc.) to an XNAT project resource.
    Creates the resource if it doesn't exist.

    Args:
        project_id (str): e.g. "BJH_ICH"
        file_path (str): full path to the file to upload
        resource_name (str): resource folder name under the project (default "AUDIT_REPORTS")

    Returns:
        dict: {"project_id": ..., "file": ..., "resource": ..., "status": ..., "response_code": int}
    """
    import os

    try:
        xnatSession.renew_httpsession()

        if not os.path.exists(file_path):
            print(f"[WARN] File not found: {file_path}")
            return {
                "project_id": project_id,
                "file": file_path,
                "resource": resource_name,
                "status": "file_not_found",
                "response_code": None,
            }

        # Ensure resource exists (PUT is idempotent)
        resource_url = f"{xnatSession.host}/data/projects/{project_id}/resources/{resource_name}"
        r = xnatSession.httpsess.put(resource_url)
        if r.status_code == 409:
            print(f"[INFO] Resource '{resource_name}' already exists for project {project_id}.")
        elif r.status_code in (200, 201):
            print(f"[INFO] Resource '{resource_name}' created for project {project_id}.")
        else:
            print(f"[WARN] Resource creation returned {r.status_code} for {project_id}.")

        # Upload the file
        file_name = os.path.basename(file_path)
        upload_url = f"{xnatSession.host}/data/projects/{project_id}/resources/{resource_name}/files/{file_name}?overwrite=true"

        headers = {"Content-Type": "application/octet-stream"}

        with open(file_path, "rb") as f:
            upload_resp = xnatSession.httpsess.put(upload_url, data=f, headers=headers)

        code = upload_resp.status_code
        if code in (200, 201, 202):
            print(f"[INFO] Uploaded '{file_name}' to resource '{resource_name}' ({code}).")
            status = "uploaded"
        else:
            print(f"[WARN] Upload failed for {file_name} (status {code}).")
            print(f"[DEBUG] Server response: {upload_resp.text[:200]}")
            status = "failed"

        return {
            "project_id": project_id,
            "file": file_path,
            "resource": resource_name,
            "status": status,
            "response_code": code,
        }

    except Exception as e:
        print(f"[ERROR] upload_project_file_to_xnat failed: {e}")
        return {
            "project_id": project_id,
            "file": file_path,
            "resource": resource_name,
            "status": "error",
            "response_code": None,
        }
def _get_resource_size_bytes(session_id: str, scan_id: str, resource_name: str):
    """
    Returns (total_bytes, file_count) for a scan resource by listing all files.
    Gracefully returns (0, 0) if resource not accessible or empty.
    """
    total = 0
    count = 0
    try:
        xnatSession.renew_httpsession()
        list_url = f"/data/experiments/{session_id}/scans/{scan_id}/resources/{resource_name}/files?format=json"
        r = xnatSession.httpsess.get(xnatSession.host + list_url)
        if r.status_code != 200:
            return 0, 0

        results = r.json().get("ResultSet", {}).get("Result", []) or []
        if not results:
            return 0, 0

        # XNAT may use different size field names; cover common cases.
        # Prefer bytes if available; otherwise coerce to int and sum.
        import pandas as pd
        df = pd.DataFrame(results)
        size_cols = [c for c in df.columns if c.lower() in {"size", "filesize", "file_size"}]
        if size_cols:
            s = pd.to_numeric(df[size_cols[0]], errors="coerce").fillna(0).astype("int64")
            total = int(s.sum())
            count = int((s > 0).sum()) if len(s) else 0
        else:
            # no size column reported; we can only report file count
            total = 0
            count = int(len(df))
        return total, count
    except Exception:
        return 0, 0


def main():
    print("WO ZAI ::{}".format("main"))
    parser = argparse.ArgumentParser()
    parser.add_argument('stuff', nargs='+')
    args = parser.parse_args()
    name_of_the_function=args.stuff[0]
    return_value=0
    if name_of_the_function == "call_check_if_a_file_exist_in_snipr":
        return_value=call_check_if_a_file_exist_in_snipr(args)
    if name_of_the_function == "project_resource_latest_analytic_file":
        print("WO ZAI ::{}".format(name_of_the_function))
        return_value=project_resource_latest_analytic_file(args)
    if name_of_the_function == "call_concatenate_csv_list":
        return_value=call_concatenate_csv_list(args)
    if name_of_the_function == "call_download_files_in_a_resource_in_a_session":
        return_value=call_download_files_in_a_resource_in_a_session(args)
    if name_of_the_function == "call_download_all_csv_files_givena_URIdf":
        return_value=call_download_all_csv_files_givena_URIdf(args)
    if name_of_the_function == "call_divide_sessionlist_done_vs_undone":
        return_value=call_divide_sessionlist_done_vs_undone(args)

    if name_of_the_function == "call_download_files_with_mastersessionlist":
        return_value=call_download_files_with_mastersessionlist(args)
    if name_of_the_function=="call_combinecsvs_inafileoflist":
        return_value=call_combinecsvs_inafileoflist(args)

    if name_of_the_function=="call_uploadfilesfromlistinacsv":
        return_value=call_uploadfilesfromlistinacsv(args)
    if name_of_the_function=="call_get_resourcefiles_metadata_saveascsv_args":
        return_value=call_get_resourcefiles_metadata_saveascsv_args(args)
    if name_of_the_function=="call_uploadsinglefile_with_URI":
        return_value=call_uploadsinglefile_with_URI(args)
    if name_of_the_function=="call_download_a_singlefile_with_URIString":
        return_value=call_download_a_singlefile_with_URIString(args)
    if name_of_the_function=="call_change_type_of_scan":
        return_value=call_change_type_of_scan(args)
    if name_of_the_function=="call_get_metadata_session":
        return_value=call_get_metadata_session(args)
    if name_of_the_function=="call_get_session_label":
        return_value=call_get_session_label(args) #
    if name_of_the_function=="call_downloadfiletolocaldir_py":
        return_value=call_downloadfiletolocaldir_py(args) #
    if name_of_the_function=="call_delete_file_with_ext":
        return_value=call_delete_file_with_ext(args)
    if name_of_the_function=="call_dowload_a_folder_as_zip":
        return_value=call_dowload_a_folder_as_zip(args)
    if name_of_the_function=="call_fill_google_mysql_db_with_single_value":
        return_value=call_fill_google_mysql_db_with_single_value(args)
    if name_of_the_function=="call_fill_google_mysql_db_from_csv":
        return_value=call_fill_google_mysql_db_from_csv(args) #
    if name_of_the_function=="call_get_session_project":
        return_value=call_get_session_project(args)
    if name_of_the_function=="call_pipeline_step_completed":
        return_value=call_pipeline_step_completed(args)
    if name_of_the_function=="call_download_a_file_with_ext":
        return_value=call_download_a_file_with_ext(args)

    print(return_value) #
    if "call" not in name_of_the_function:
        globals()[args.stuff[0]](args)
    xnatSession.close_httpsession()
    return return_value
if __name__ == '__main__':
    main()
