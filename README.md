## to use this you need to have access to https://snipr.wustl.edu/.
---
SNIPR command to run prepocessing before segmenation: "ct_processing_before_segmentation"
output: html_document
---

> **Note:** `eval=FALSE` prevents accidental deletion of files. Set `eval=TRUE` to execute.

```{bash, eval=FALSE}
# 1) Docker image
imagename='registry.nrg.wustl.edu/docker/nrg-repo/sharmaatul11/yashengstep1:latest'

# 2) Create directories
mkdir working input ZIPFILEDIR output NIFTIFILEDIR DICOMFILEDIR software workinginput workingoutput outputinsidedocker

# 3) Clean old contents
rm -r working/* input/* ZIPFILEDIR/* output/* NIFTIFILEDIR/* DICOMFILEDIR/* software/* workinginput/* workingoutput/* outputinsidedocker/*

# 4) Set XNAT variables
SESSION_ID=REPLACE_WITH_SESSION_ID   # e.g., SNIPR_E03614
PROJECT=REPLACE_WITH_PROJECT_NAME    # e.g., SNIPR01
XNAT_USER=REPLACE_WITH_XNAT_USERNAME
XNAT_PASS=REPLACE_WITH_XNAT_PASSWORD
XNAT_HOST='https://snipr.wustl.edu'

# 5) Run Docker container
docker run \
  -v $PWD/output:/output \
  -v $PWD/input:/input \
  -v $PWD/ZIPFILEDIR:/ZIPFILEDIR \
  -v $PWD/software:/software \
  -v $PWD/NIFTIFILEDIR:/NIFTIFILEDIR \
  -v $PWD/DICOMFILEDIR:/DICOMFILEDIR \
  -v $PWD/working:/working \
  -v $PWD/workinginput:/workinginput \
  -v $PWD/workingoutput:/workingoutput \
  -v $PWD/outputinsidedocker:/outputinsidedocker \
  -it ${imagename} \
  /callfromgithub/downloadcodefromgithub.sh \
    ${SESSION_ID} \
    ${XNAT_USER} \
    ${XNAT_PASS} \
    ${XNAT_HOST} \
    https://github.com/dharlabwustl/CT_PROCESSING_STEP1.git \
    2
```

SNIPR command to run after segmenation: "ct_processing_after_segmentation"
output: html_document
---

> **Note:** `eval=FALSE` prevents accidental deletion of files. Set `eval=TRUE` to execute.

```{bash, eval=FALSE}
# 1) Docker image
imagename='registry.nrg.wustl.edu/docker/nrg-repo/sharmaatul11/yashengstep1:latest'

# 2) Create directories
mkdir working input ZIPFILEDIR output NIFTIFILEDIR DICOMFILEDIR software workinginput workingoutput outputinsidedocker

# 3) Clean old contents
rm -r working/* input/* ZIPFILEDIR/* output/* NIFTIFILEDIR/* DICOMFILEDIR/* software/* workinginput/* workingoutput/* outputinsidedocker/*

# 4) Set XNAT variables
SESSION_ID=REPLACE_WITH_SESSION_ID   # e.g., SNIPR_E03614
PROJECT=REPLACE_WITH_PROJECT_NAME    # e.g., SNIPR01
XNAT_USER=REPLACE_WITH_XNAT_USERNAME
XNAT_PASS=REPLACE_WITH_XNAT_PASSWORD
XNAT_HOST='https://snipr.wustl.edu'

# 5) Run Docker container
docker run \
  -v $PWD/output:/output \
  -v $PWD/input:/input \
  -v $PWD/ZIPFILEDIR:/ZIPFILEDIR \
  -v $PWD/software:/software \
  -v $PWD/NIFTIFILEDIR:/NIFTIFILEDIR \
  -v $PWD/DICOMFILEDIR:/DICOMFILEDIR \
  -v $PWD/working:/working \
  -v $PWD/workinginput:/workinginput \
  -v $PWD/workingoutput:/workingoutput \
  -v $PWD/outputinsidedocker:/outputinsidedocker \
  -it ${imagename} \
  /callfromgithub/downloadcodefromgithub.sh \
    ${SESSION_ID} \
    ${XNAT_USER} \
    ${XNAT_PASS} \
    ${XNAT_HOST} \
    https://github.com/dharlabwustl/CT_PROCESSING_STEP1.git \
    1


```

