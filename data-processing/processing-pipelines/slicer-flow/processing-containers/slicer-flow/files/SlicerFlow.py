import json
import os
# bug workaround
# https://discourse.slicer.org/t/slicer-often-crashes-when-running-with-python-script-in-loading/23719/3
slicer.app.processEvents()
from DICOMLib import DICOMUtils

workflow_dir = os.getenv('WORKFLOW_DIR')
fn_tasklist = os.path.join(workflow_dir, 'batch/tasklist.json')
dir_base = os.path.join(workflow_dir,'batch')
print(workflow_dir)

slicer.app.processEvents()

f = open(fn_tasklist)
j = json.load(f)
#print(j)
fn_image = j['Tasks'][0]['Image']
fn_result=j['Tasks'][0]['Result']
dag_task_name=j['Tasks'][0]['Name']

print(fn_image)
print(fn_result)
print(dag_task_name)

slicer.app.processEvents()

fn_image_full = os.path.join(dir_base, fn_image)
if os.path.exists(fn_image_full):
    print('found input image')
dicomDataDir = os.path.dirname(fn_image_full)

slicer.app.processEvents()

# create output directory for DAG to pick up results from
# permissions on parent set in startSlicer.sh
# executed as user slicer
# expected path is WORKFLOW_DIR/batch/1.2.3.xxxx/slicer-results
dir_slicer_results = os.path.join(os.path.split(dicomDataDir)[0],'slicer-results')
slicer.app.processEvents()
if not os.path.exists(dir_slicer_results):
    os.mkdir(dir_slicer_results)

slicer.app.processEvents()
#
# reading DICOM files into Slicer scene
# https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#dicom
# dicomDataDir = "c:/my/folder/with/dicom-files"  # input folder with DICOM files
loadedNodeIDs = []  # this list will contain the list of all loaded node IDs
slicer.app.processEvents()

with DICOMUtils.TemporaryDICOMDatabase() as db:
    DICOMUtils.importDicom(dicomDataDir, db)
    slicer.app.processEvents()
    patientUIDs = db.patients()
    slicer.app.processEvents()
    for patientUID in patientUIDs:
        loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))
        slicer.app.processEvents()

