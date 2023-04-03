echo '==============================='
echo 'Run Slicer'
echo '==============================='
echo "slicer" | sudo -S chown slicer:slicer -R /$WORKFLOW_DIR/$BATCH_NAME
# this is for the future(?)
# echo "slicer" | sudo -S chown slicer:slicer -R /$AIRFLOW_WORKFLOW_DIR/$BATCH_NAME
# slicer-results can be also created from within SlicerFlow.py
# mkdir /$WORKFLOW_DIR/$BATCH_NAME/slicer-results

# install slicer extensions
/opt/slicer/Slicer --python-script /opt/slicer/install-slicer-extension.py --no-splash --no-main-window

# old-style start with DICOM files loaded from DAG-created folder:
#/opt/slicer/Slicer --no-splash --python-script /opt/slicer/SlicerFlow.py 

# loading the mpReview module at Slicer startup
/opt/slicer/Slicer --no-splash --additional-module-paths /opt/slicer/mpReview

# MITK flow example below from startMITK.sh
#/mitk/MitkFlowBench.sh /$WORKFLOW_DIR/$BATCH_NAME/tasklist.json
#PID=$!
# wait until Workbench is ready
#tail -f  /home/mitk/Desktop/logfile | while read LOGLINE
#do
#	[[ "${LOGLINE}" == *"BlueBerry Workbench ready"* ]] && pkill -P $$ tail
#done
#echo 'Setting fullscreen mode'
#wmctrl -r 'Segmentation' -b toggle,fullscreen
# wait for process to end, before starting new process
#wait $PID
#clear logfile
#> /home/mitk/Desktop/logfile
