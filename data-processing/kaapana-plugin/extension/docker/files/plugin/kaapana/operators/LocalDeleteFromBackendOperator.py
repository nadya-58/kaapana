import glob
import json
import os
from pathlib import Path

import pydicom
import requests

from kaapana.blueprints.kaapana_global_variables import SERVICES_NAMESPACE
from kaapana.operators.KaapanaPythonBaseOperator import KaapanaPythonBaseOperator


class LocalDeleteFromBackendOperator(KaapanaPythonBaseOperator):
    """
    Operator to remove series from backend.

    **Inputs:**

    * Input data which should be removed is given via input parameter: delete_operator.
    """

    def start(self, ds, **kwargs):
        run_dir = os.path.join(self.airflow_workflow_dir, kwargs['dag_run'].run_id)
        batch_folder = [f for f in glob.glob(os.path.join(run_dir, self.batch_name, '*'))]

        for batch_element_dir in batch_folder:
            dcm_files = sorted([*Path(batch_element_dir, self.operator_in_dir).rglob("*.dcm*")])
            if len(dcm_files) > 0:
                incoming_dcm = pydicom.dcmread(dcm_files[0])
                series_uid = incoming_dcm.SeriesInstanceUID
                resp = requests.delete(
                    f'http://kaapana-backend-service.{SERVICES_NAMESPACE}.svc:5000/client/identifier?identifier={series_uid}'
                )
                if resp.status_code == 404:
                    print('Item not found in database. This might happen when an item was not used in a Dataset/Cohort')
                elif resp.status_code != 200:
                    print(f'Failed to delete {series_uid} from backend with: [{resp.status_code}] {resp.text}')
                    exit(1)
            else:
                json_files = sorted([*Path(batch_element_dir, self.operator_in_dir).rglob("*.json*")])
                for meta_files in json_files:
                    with open(meta_files) as fs:
                        metadata = json.load(fs)
                        series_uid = metadata['0020000E SeriesInstanceUID_keyword']
                        resp = requests.delete(
                            f'http://kaapana-backend-service.{SERVICES_NAMESPACE}.svc:5000/client/identifier?identifier={series_uid}'
                        )
                        if resp.status_code == 404:
                            print(
                                'Item not found in database. This might happen when '
                                'an item was not used in a Dataset/Cohort'
                            )
                        elif resp.status_code != 200:
                            print(f'Failed to delete {series_uid} from backend with: [{resp.status_code}] {resp.text}')
                            exit(1)

    def __init__(self,
                 dag,
                 delete_operator=None,
                 **kwargs):
        """
        :param delete_operator:
        """

        super().__init__(
            dag=dag,
            name='delete-backend',
            python_callable=self.start,
            **kwargs
        )
