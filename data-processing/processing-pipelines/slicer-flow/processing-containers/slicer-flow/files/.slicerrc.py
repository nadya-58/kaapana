import json
import os

# initialize Slicer DICOM local database 
documentsLocation = qt.QStandardPaths.DocumentsLocation
documents = qt.QStandardPaths.writableLocation(documentsLocation)
databaseDirectory = os.path.join(documents, slicer.app.applicationName + "DICOMDatabase")
dicomBrowser = ctk.ctkDICOMBrowser()
dicomBrowser.databaseDirectory = databaseDirectory
dicomBrowser.createNewDatabaseDirectory()

# read input tasklist from Kaapana

workflow_dir = os.getenv('WORKFLOW_DIR')

fn_tasklist = os.path.join(workflow_dir,'batch/tasklist.json')
if not os.path.exists(fn_tasklist):
    print('tasklist not found', fn_tasklist)
    exit(1) # does slicer honor exit(1) in .slicerrc.py ??
print('found tasklist: ', fn_tasklist)
f = open(fn_tasklist)
j = json.load(f)
f.close()

# create Kaapana-specific config file for mpReview

dicom_url = "http://dcm4chee-service.services.svc:8080/dcm4chee-arc/aets/KAAPANA/rs"
kaapana_db = {"project_id": "", "location_id": "", "dataset_id": "",\
        "dicomstore_id": "", "other_server_url": dicom_url}

# mpReview needs SeriesInstanceUIDs grouped by their StudyIntanceUID; tasklist.json is flat
uids = []
studies_all = list(set( [ t['StudyInstanceUID'] for t in j['Tasks'] ] ))
print('found', len(studies_all), 'studies')
for study in studies_all:
    series_list  = []
    for t in j['Tasks']:
        if t['StudyInstanceUID'] == study:
            series_list.append( t['SeriesUID'] )
    uids.append({'StudyInstanceUID': study, 'SeriesInstanceUID_list': series_list})
    print( len(series_list), 'series for study', study)

# output mapping is a flat list by SeriesInstanceUID just as tasklist.json
output_mapping = []
for t in j['Tasks']:
    output_mapping.append( { "SeriesInstanceUID": t["SeriesUID"], "output_file": t["Result"]  })

output_cfg = { "output_directory": os.path.join(workflow_dir,'batch'), "output_mapping" : output_mapping}

mpReviewConfig = { "username": "sliceruser", "database_type": "remote",\
        "remote_database_configuration" : kaapana_db,\
        "uids": uids,\
        "output_configuration": output_cfg,\
        "terminology": "SegmentationCategoryTypeModifier-mpReview.json"}

json_out = json.dumps(mpReviewConfig, indent=4)

# write out the json file
# file name is defined in mpReview.py; assume the directory is writable
mpReviewConfig_dir = "/opt/slicer/mpReview/Resources"
mpReviewConfig_fn = "mpReview_remote_kaapana_configuration_hierarchy2.json"
fn_out = os.path.join(mpReviewConfig_dir, mpReviewConfig_fn)
with open(fn_out, "w") as f:
    json.dump(mpReviewConfig, f)

