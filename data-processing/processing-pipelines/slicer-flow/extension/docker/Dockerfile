FROM local-only/base-installer:latest

LABEL IMAGE="dag-slicer-flow"
LABEL VERSION="2022.10"
LABEL CI_IGNORE="False"

COPY files/dag_slicer_flow.py /kaapana/tmp/dags/
COPY files/slicer_flow /kaapana/tmp/dags/slicer_flow

RUN touch /kaapana/tmp/dags/dag_slicer_flow.py

