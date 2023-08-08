from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
from datetime import timedelta
from airflow.models import DAG
from slicer_flow.SlicerInputOperator import SlicerInputOperator
from kaapana.operators.LocalWorkflowCleanerOperator import LocalWorkflowCleanerOperator
from kaapana.operators.LocalGetInputDataOperator import LocalGetInputDataOperator
from kaapana.operators.KaapanaApplicationOperator import KaapanaApplicationOperator
from kaapana.operators.DcmSendOperator import DcmSendOperator
from kaapana.blueprints.kaapana_global_variables import KAAPANA_BUILD_VERSION
from datetime import datetime

import os

log = LoggingMixin().log

dag_info = {
    "ui_visible": True,
}

ui_forms = {
    "workflow_form": {
        "type": "object",
        "properties": {
            "single_execution": {
                "title": "single execution",
                "description": "Should each series be processed separately?",
                "type": "boolean",
                "default": False,
                "readOnly": False,
            }
        }
    }
}

args = {
    'ui_visible': True,
    'ui_forms': ui_forms,
    'owner': 'kaapana',
    'start_date': days_ago(0),
    'retries': 1,
    'retry_delay': timedelta(seconds=30)
}

dag = DAG(
    dag_id='slicer-flow',
    default_args=args,
    concurrency=10,
    max_active_runs=5,
    schedule_interval=None
)

#get_input = LocalGetInputDataOperator(dag=dag)
get_input = LocalGetInputDataOperator(dag=dag, data_type="json")
slicer_input = SlicerInputOperator(dag=dag, input_operator=get_input, operator_out_dir="slicer-results")
launch_app = KaapanaApplicationOperator(dag=dag,
                                        name="application-slicer-flow",
                                        input_operator=get_input,
                                        chart_name='slicer-flow-chart',
                                        version=KAAPANA_BUILD_VERSION)
send_dicom = DcmSendOperator(dag=dag, operator_in_dir="slicer-results", ae_title="Slicer-flow")
clean = LocalWorkflowCleanerOperator(dag=dag)


get_input >> slicer_input >> launch_app >> send_dicom >> clean
#get_input >> launch_app >> send_dicom >> clean
