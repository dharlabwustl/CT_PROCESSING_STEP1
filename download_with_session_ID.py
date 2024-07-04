#!/usr/bin/python

import os, sys, errno, shutil, uuid,subprocess,csv,json
import math,inspect
import glob
import re
import requests
import pandas as pd
import nibabel as nib
import argparse
# import pydicom as dicom
import pathlib,xmltodict
from xnatSession import XnatSession
from redcapapi_functions import *
catalogXmlRegex = re.compile(r'.*\.xml$')
XNAT_HOST_URL=os.environ['XNAT_HOST']  # 'https://snipr02.nrg.wustl.edu:8080' #'https://snipr02.nrg.wustl.edu' # 'https://snipr.wustl.edu'
XNAT_HOST = XNAT_HOST_URL # os.environ['XNAT_HOST']  #
XNAT_USER = os.environ['XNAT_USER']#
XNAT_PASS =os.environ['XNAT_PASS'] #
api_token=os.environ['REDCAP_API']
def combinecsvs(inputdirectory,outputdirectory,outputfilename,extension):
    outputfilepath=os.path.join(outputdirectory,outputfilename)
    # extension = 'csv'
    all_filenames = [i for i in glob.glob(os.path.join(inputdirectory,'*{}'.format(extension)))]
#    os.chdir(inputdirectory)
    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    #export to csv
    combined_csv.to_csv(outputfilepath, index=False, encoding='utf-8-sig')

def call_combine_all_csvfiles_of_edema_biomarker():
    working_directory=sys.argv[1]
    working_directory_tocombinecsv=sys.argv[2]
    extension=sys.argv[3]
    outputfilename=sys.argv[4]
    combinecsvs(working_directory,working_directory_tocombinecsv,outputfilename,extension)

def call_get_all_selected_scan_in_a_project():
    projectId=sys.argv[1]
    working_directory=sys.argv[2]
    get_all_selected_scan_in_a_project(projectId,working_directory)


def call_get_all_EDEMA_BIOMARKER_csvfiles_of_allselectedscan():
    working_directory=sys.argv[1]
    get_all_EDEMA_BIOMARKER_csvfiles_of_ascan(working_directory)
    
    
    
def get_all_EDEMA_BIOMARKER_csvfiles_of_ascan(dir_to_receive_the_data):
    for each_csvfile in glob.glob(os.path.join(dir_to_receive_the_data,'SNIPR*.csv')):
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
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    xnatSession.close_httpsession()
    sessions_list=response.json()['ResultSet']['Result']
    
    return sessions_list
def call_decision_which_nifti():
    sessionId=sys.argv[1]
    dir_to_receive_the_data=sys.argv[2]
    output_csvfile=sys.argv[3]
    decision_which_nifti(sessionId,dir_to_receive_the_data,output_csvfile)
    
def decision_which_nifti(sessionId,dir_to_receive_the_data="",output_csvfile=""):
    print("I AM HERE:decision_which_nifti")
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
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] == 'usable')] ##| (df['type'] == 'Z-Brain-Thin')]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin')  & (df['quality'] == 'usable') ] ##| (df['type'] == 'Z-Brain-Thin')]
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
                    list_of_usables_withsize.append([each_nifti['URI'],each_nifti['Name'],each_axial['ID'],number_slice])
                    deleteafile(os.path.join(dir_to_receive_the_data,x[1]))
  
                    
                    
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
                print(each_nifti['URI'])
                if '.nii' in each_nifti['Name'] or '.nii.gz' in each_nifti['Name']:
                    x=[each_nifti['URI'],each_nifti['Name'],each_thin['ID']]
                    list_of_usables.append([each_nifti['URI'],each_nifti['Name'],each_thin['ID']])
                    x=[each_nifti['URI'],each_nifti['Name'],each_thin['ID']]
                    downloadniftiwithuri(x,dir_to_receive_the_data)
                    number_slice=nifti_number_slice(os.path.join(dir_to_receive_the_data,x[1]))
                    list_of_usables_withsize.append([each_nifti['URI'],each_nifti['Name'],each_thin['ID'],number_slice])
                    deleteafile(os.path.join(dir_to_receive_the_data,x[1]))                    
  
            # break
    # dir_to_receive_the_data="./NIFTIFILEDIR"
    # final_ct_file=list_of_usables[0]
    if len(list_of_usables_withsize) > 0:
        jsonStr = json.dumps(list_of_usables_withsize)
        # print(jsonStr)
        df = pd.read_json(jsonStr)
        df.columns=['URI','Name','ID','NUMBEROFSLICES']
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
            pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
            return True
        return False
    else:
        return False
def nifti_number_slice(niftifilename):
    return nib.load(niftifilename).shape[2]

    # pd.DataFrame(final_ct_file).T.to_csv(os.path.join(dir_to_receive_the_data,output_csvfile),index=False)
# def downloadniftiwithuri(URI,dir_to_save,niftioutput_filename):
#     xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
#     # for x in range(df.shape[0]):
#     #     print(df.iloc[x])
        
#     url =   URI #  df.iloc[0][0] #URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" % 
#         # (sessionId, scanId))
#     print(url)
#     xnatSession.renew_httpsession()
#     response = xnatSession.httpsess.get(xnatSession.host + url)
#     zipfilename=os.path.join(dir_to_save,niftioutput_filename) #sessionId+scanId+'.zip'
#     with open(zipfilename, "wb") as f:
#         for chunk in response.iter_content(chunk_size=512):
#             if chunk:  # filter out keep-alive new chunks
#                 f.write(chunk)
#     xnatSession.close_httpsession()
    
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
    df_axial=df.loc[(df['type'] == 'Z-Axial-Brain') & (df['quality'] == 'usable') ] ##| (df['type'] == 'Z-Brain-Thin')]
    df_thin=df.loc[(df['type'] == 'Z-Brain-Thin') & (df['quality'] == 'usable')] ##| (df['type'] == 'Z-Brain-Thin')]
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
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    for x in range(df.shape[0]):
        print(df.iloc[x])
        
        url =     df.iloc[x][0] #URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" % 
            # (sessionId, scanId))
        print(url)
        xnatSession.renew_httpsession()
        response = xnatSession.httpsess.get(xnatSession.host + url)
        zipfilename=os.path.join(dir_to_save,df.iloc[x][1]) #sessionId+scanId+'.zip'
        with open(zipfilename, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        xnatSession.close_httpsession()
        
def downloadmaskswithuri_withcsv():
    csvfilename=sys.argv[1]
    dir_to_save=sys.argv[2]
    df=pd.read_csv(csvfilename) 
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    for item_id, each_scan in df.iterrows():
        # print("each_scan['URI'] {}".format(each_scan['URI']))    
    # for x in range(df.shape[0]):
        # print(df.iloc[x])
        
        url =  each_scan['URI'] #   df.iloc[0][0] #URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" % 
            # (sessionId, scanId))
        print(url)
        xnatSession.renew_httpsession()
        response = xnatSession.httpsess.get(xnatSession.host + url)
        zipfilename=os.path.join(dir_to_save,each_scan['Name']) #sessionId+scanId+'.zip'
        with open(zipfilename, "wb") as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        xnatSession.close_httpsession()
def downloadresourcefilewithuri_py(url,dir_to_save):
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url['URI'])
    zipfilename=os.path.join(dir_to_save,url['Name']) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    xnatSession.close_httpsession()
    
def downloadniftiwithuri(URI_name,dir_to_save):
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    url = URI_name[0] #("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" % 
        # (sessionId, scanId))
    print(url)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    zipfilename=os.path.join(dir_to_save,URI_name[1]) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    xnatSession.close_httpsession()

def get_niftifiles_metadata(URI):
    url = (URI+'/resources/NIFTI/files?format=json')
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    xnatSession.close_httpsession()
    metadata_nifti=response.json()['ResultSet']['Result']
    return metadata_nifti
def get_resourcefiles_metadata(URI,resource_dir):
    url = (URI+'/resources/' + resource_dir +'/files?format=json')
    print(url)
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    xnatSession.close_httpsession()
    metadata_masks=response.json()['ResultSet']['Result']
    return metadata_masks

def findthetargetscan():
     target_scan=""
     ## find the list of usable scans
     ## Is axial available? If yes, focus on axial, if not go for thin
     ## Is tilt available ? If yes, get the tilt, if not go for non-tilt
     return target_scan

def uploadfile():
    print("FILE UPLOADED:{}".format('uploadfile'))
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    input_dirname=str(sys.argv[3])
    resource_dirname=str(sys.argv[4])
    file_suffix=str(sys.argv[5])
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    url = (("/data/experiments/%s/scans/%s/resources/"+resource_dirname+"/files/") % (sessionId, scanId))
    allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
    for eachniftifile in allniftifiles:
        files={'file':open(eachniftifile,'rb')}
        response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
        print(response)
        print("FILE UPLOADED:{}".format(eachniftifile))
    xnatSession.close_httpsession()
    # for eachniftifile in allniftifiles:
    #     command= 'rm  ' + eachniftifile
    #     subprocess.call(command,shell=True)

    return True 

def uploadfile_projectlevel():
    try:
        projectId=str(sys.argv[1])
        input_dirname=str(sys.argv[2])
        resource_dirname=str(sys.argv[3])
        file_suffix=str(sys.argv[4])
        xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        xnatSession.renew_httpsession()
        url = (("/data/projects/%s/resources/"+resource_dirname+"/files/") % (projectId))
        allniftifiles=glob.glob(os.path.join(input_dirname,'*'+file_suffix) ) #input_dirname + '/*'+file_suffix)
        for eachniftifile in allniftifiles:
            files={'file':open(eachniftifile,'rb')}
            response = xnatSession.httpsess.post(xnatSession.host + url,files=files)
            print(response)
        xnatSession.close_httpsession()
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
        xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        xnatSession.renew_httpsession()
        outcome=get_nifti_using_xnat(sessionId, scanId)
        if outcome==False:
            print("NO DICOM FILE %s:%s:%s:%s" % (sessionId, scanId))
        xnatSession.close_httpsession()
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
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    outcome=get_nifti_using_xnat(sessionId, scanId)
    if outcome==False:
        print("NO DICOM FILE %s:%s:%s:%s" % (sessionId, scanId))
    xnatSession.close_httpsession()
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

def get_metadata_session(sessionId):
    url = ("/data/experiments/%s/scans/?format=json" %    (sessionId))
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    xnatSession.close_httpsession()
    metadata_session=response.json()['ResultSet']['Result']
    return metadata_session
def get_metadata_session_forbash():
    sessionId=sys.argv[1]
    url = ("/data/experiments/%s/scans/?format=json" %    (sessionId))
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    xnatSession.close_httpsession()
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
            if 'usable' in result_usability.lower():
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




def get_nifti_using_xnat(sessionId, scanId):
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    url = ("/data/experiments/%s/scans/%s/resources/NIFTI/files?format=zip" % 
        (sessionId, scanId))

    xnatSession.renew_httpsession()
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



def downloadfiletolocaldir():
    print(sys.argv)
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    resource_dirname=str(sys.argv[3])
    output_dirname=str(sys.argv[4])

    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    url = (("/data/experiments/%s/scans/%s/resources/" + resource_dirname+ "/files?format=zip")  % 
        (sessionId, scanId))

    xnatSession.renew_httpsession()
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
    xnatSession.close_httpsession()
    copy_nifti_to_a_dir(output_dirname)

    return True

def downloadallfiletolocaldir():
    print(sys.argv)
    sessionId=str(sys.argv[1])
    scanId=str(sys.argv[2])
    resource_dirname=str(sys.argv[3])
    output_dirname=str(sys.argv[4])

    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    url = (("/data/experiments/%s/scans/%s/resources/" + resource_dirname+ "/files?format=zip")  %
           (sessionId, scanId))

    xnatSession.renew_httpsession()
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
    xnatSession.close_httpsession()
    copy_allfiles_to_a_dir(output_dirname)

    return True
# def downloadfiletolocaldir_py(sessionId,scanId,resource_dirname,output_dirname):
#     xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
#     url = (("/data/experiments/%s/scans/%s/resources/" + resource_dirname+ "/files?format=zip")  % 
#         (sessionId, scanId))

#     xnatSession.renew_httpsession()
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
#     xnatSession.close_httpsession()
#     copy_nifti_to_a_dir(output_dirname)

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
def copy_allfiles_to_a_dir(dir_name):
    for dirpath, dirnames, files in os.walk('/ZIPFILEDIR'):
        #                print(f'Found directory: {dirpath}')
        for file_name in files:
            # file_extension = pathlib.Path(file_name).suffix
            # if 'nii' in file_extension or 'gz' in file_extension:
            command='cp ' + os.path.join(dirpath,file_name) + '  ' + dir_name + '/'
            subprocess.call(command,shell=True)
            print(os.path.join(dirpath,file_name))
def check_if_a_file_exist_in_snipr(URI, resource_dir,extension_to_find_list):
    url = (URI+'/resources/' + resource_dir +'/files?format=json')
    # print("url::{}".format(url))
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    response = xnatSession.httpsess.get(xnatSession.host + url)
    num_files_present=0
    if response.status_code != 200:
        xnatSession.close_httpsession()
        return num_files_present
    metadata_masks=response.json()['ResultSet']['Result']
    # print("metadata_masks::{}".format(metadata_masks))
    df_scan = pd.read_json(json.dumps(metadata_masks))
    for extension_to_find in extension_to_find_list:
        for x in range(df_scan.shape[0]):
            # print(df_scan.loc[x,'Name'])
            if extension_to_find in df_scan.loc[x,'Name']:
                num_files_present=num_files_present+1
                break
    return num_files_present
def call_check_if_a_file_exist_in_snipr( args):
    # parser = argparse.ArgumentParser()
    # parser.add_argument('stuff', nargs='+')
    # args = parser.parse_args()
    # print (args.stuff)
    sessionID=args.stuff[1]
    scanID=args.stuff[2]
    resource_dir=args.stuff[3]
    URI="/data/experiments/"+sessionID+"/scans/"+scanID
    extension_to_find_list=args.stuff[4:]
    file_present=check_if_a_file_exist_in_snipr(URI, resource_dir,extension_to_find_list)
    all_files_present_flag=0
    if file_present < len(extension_to_find_list):
        return 0
    else:
        all_files_present_flag=1
    all_files_present_flag_df=pd.DataFrame([all_files_present_flag])
    all_files_present_flag_df.columns=['all_files_present_flag']
    all_files_present_flag_df.to_csv('/workinginput/all_files_present_flag_df.csv',index=False)
    return 1
def listoffile_witha_URI_as_df(URI):
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    # print("I AM IN :: listoffile_witha_URI_as_df::URI::{}".format(URI))
    response = xnatSession.httpsess.get(xnatSession.host + URI)
    # print("I AM IN :: listoffile_witha_URI_as_df::URI::{}".format(URI))
    num_files_present=0
    df_scan=[]
    if response.status_code != 200:
        xnatSession.close_httpsession()
        return num_files_present
    metadata_masks=response.json()['ResultSet']['Result']
    df_listfile = pd.read_json(json.dumps(metadata_masks))
    xnatSession.close_httpsession()
    return df_listfile
def download_a_singlefile_with_URIString(url,filename,dir_to_save):
    xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
    xnatSession.renew_httpsession()
    # command="echo  " + url['URI'] + " >> " +  os.path.join(dir_to_save,"test.csv")
    # subprocess.call(command,shell=True)
    response = xnatSession.httpsess.get(xnatSession.host +url) #/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv") #
    #                                                       # "/data/experiments/SNIPR02_E03548/scans/1-CT1/resources/147851/files/ICH_0001_01022017_0414_1-CT1_threshold-1024.0_22121.0TOTAL_VersionDate-11302022_04_22_2023.csv") ## url['URI'])
    zipfilename=os.path.join(dir_to_save,filename ) #"/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv")) #sessionId+scanId+'.zip'
    with open(zipfilename, "wb") as f:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    xnatSession.close_httpsession()
    return zipfilename
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
def call_download_files_in_a_resource_in_a_session(args):
    sessionId=args.stuff[1]
    # scanId=args.stuff[2]
    resource_dirname=args.stuff[2]
    dir_to_save=args.stuff[3]
    URI = (("/data/experiments/%s/resources/" + resource_dirname+ "/files?format=json")  %
           (sessionId))

    try:
        download_files_in_a_resource(URI,dir_to_save)
        print("I AM IN :: call_download_files_in_a_resource_in_a_session::URI::{}".format(URI))
        return 1
    except:
        return 0
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
        xnatSession = XnatSession(username=XNAT_USER, password=XNAT_PASS, host=XNAT_HOST)
        xnatSession.renew_httpsession()

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
        # xnatSession.close_httpsession()
        # return num_files_present



        # zipfilename=os.path.join(dir_to_save,filename ) #"/data/projects/ICH/resources/179772/files/ICH_CTSESSIONS_202305170753.csv")) #sessionId+scanId+'.zip'
        # with open(zipfilename, "wb") as f:
        #     for chunk in response.iter_content(chunk_size=512):
        #         if chunk:  # filter out keep-alive new chunks
        #             f.write(chunk)
        xnatSession.close_httpsession()
        returnvalue=1
        subprocess.call("echo " + "I PASSED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        print("I PASSED AT ::{}".format(inspect.stack()[0][3]))
    except:

        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        print("I PASSED AT ::{}".format(inspect.stack()[0][3]))
    return returnvalue

def fill_redcap_for_selected_scan(args):
    try:
        # session_id=args.stuff[1]
        xmlfile=args.stuff[1]
        csv_file_df=pd.read_csv(args.stuff[2])
        project_name,subject_name, session_label,acquisition_site_xml,acquisition_datetime_xml,scanner_from_xml,body_part_xml,kvp_xml=get_info_from_xml(xmlfile)
        this_project_redcapfile_latest=project_name+'_latest.csv'
        # api_token='EC6A2206FF8C1D87D4035E61C99290FF'
        df_scan_latest=download_latest_redcapfile(api_token,this_project_redcapfile_latest)
        this_session_redcap_repeat_instance_df=df_scan_latest[df_scan_latest['snipr_session']==session_label]
        this_session_redcap_repeat_instance=str(this_session_redcap_repeat_instance_df['redcap_repeat_instance'].item())
        imaging_data_complete=str(this_session_redcap_repeat_instance_df['imaging_data_complete'].item())
        if imaging_data_complete !='2':
            for each_colname in csv_file_df.columns:
                subprocess.call("echo " + "I zai zeli AT ::{}  >> /workingoutput/error.txt".format(xmlfile) ,shell=True )
                subprocess.call("echo " + "I zai zeli AT ::{}  >> /workingoutput/error.txt".format(args.stuff[2]) ,shell=True )
                subprocess.call("echo " + "I PASSED AT subject_name::{}  >> /workingoutput/error.txt".format(subject_name) ,shell=True )
                subprocess.call("echo " + "I PASSED AT this_session_redcap_repeat_instance::{}  >> /workingoutput/error.txt".format(this_session_redcap_repeat_instance) ,shell=True )
                subprocess.call("echo " + "I PASSED AT session_label::{}  >> /workingoutput/error.txt".format(session_label) ,shell=True )
                subprocess.call("echo " + "I PASSED AT each_colname::{}  >> /workingoutput/error.txt".format(each_colname) ,shell=True )
                subprocess.call("echo " + "I PASSED AT each_colname_value::{}  >> /workingoutput/error.txt".format(csv_file_df[each_colname][0]) ,shell=True )
                try:
                    add_one_data_to_redcap(subject_name,'imaging_data',this_session_redcap_repeat_instance,str(each_colname),csv_file_df[each_colname].item())
                except:
                    pass
    except:
        subprocess.call("echo " + "I FAILED AT ::{}  >> /workingoutput/error.txt".format(inspect.stack()[0][3]) ,shell=True )
        pass
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

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('stuff', nargs='+')
    args = parser.parse_args()
    name_of_the_function=args.stuff[0]
    return_value=0
    if name_of_the_function == "call_check_if_a_file_exist_in_snipr":
        return_value=call_check_if_a_file_exist_in_snipr(args)
    if name_of_the_function == "call_download_files_in_a_resource_in_a_session":
        return_value=call_download_files_in_a_resource_in_a_session(args)
        # print(return_value)
        # return
    if "call" not in name_of_the_function:
        globals()[args.stuff[0]](args)
    print(return_value)
if __name__ == '__main__':
    main()
