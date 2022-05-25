import os
import shutil
import glob
import time
import secrets
import json
import requests
from airflow.exceptions import AirflowException
from datetime import timedelta
from kaapana.operators.KaapanaPythonBaseOperator import KaapanaPythonBaseOperator, rest_self_udpate
from kaapana.blueprints.kaapana_global_variables import BATCH_NAME, WORKFLOW_DIR
from kaapana.blueprints.kaapana_utils import cure_invalid_name

from kaapana.operators.KaapanaBaseOperator import KaapanaBaseOperator, default_registry, default_platform_abbr, default_platform_version


class KaapanaApplicationOperator(KaapanaPythonBaseOperator):
    HELM_API = 'http://kube-helm-service.kube-system.svc:5000'
    TIMEOUT = 60 * 60 * 12

    @staticmethod
    def _get_release_name(kwargs):
        task_id = kwargs['ti'].task_id
        run_id = kwargs['run_id']
        release_name = f'kaapanaint-{run_id}'
        return cure_invalid_name(release_name, r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*",
                                 max_length=53)

    def rest_sets_update(self, payload):
        operator_conf = {}
        if 'global' in payload:
            operator_conf.update(payload['global'])
        if 'operators' in payload and self.name in payload['operators']:
            operator_conf.update(payload['operators'][self.name])

        for k, v in operator_conf.items():
            self.sets[k] = str(v)

    @rest_self_udpate
    def start(self, ds, **kwargs):
        print(kwargs)
        release_name = KaapanaApplicationOperator._get_release_name(kwargs) if self.release_name is None else self.release_name

        payload = {
            'name': f'{self.chart_name}',
            'version': self.version,
            'release_name': release_name,
            'sets': {
                'mount_path': f'{self.data_dir}/{kwargs["run_id"]}',
                "workflow_dir": str(WORKFLOW_DIR),
                "batch_name": str(BATCH_NAME),
                "operator_out_dir": str(self.operator_out_dir),
                "operator_in_dir": str(self.operator_in_dir),
                "batches_input_dir": "/{}/{}".format(WORKFLOW_DIR, BATCH_NAME)
            }
        }

        if kwargs["dag_run"] is not None and 'rest_call' in kwargs["dag_run"].conf and kwargs["dag_run"].conf['rest_call'] is not None:
            self.rest_sets_update(kwargs["dag_run"].conf['rest_call']) 
            print("CHART INSTALL SETS:")
            print(json.dumps(self.sets, indent=4, sort_keys=True))

        for set_key, set_value in self.sets.items():
            payload['sets'][set_key] = set_value

        url = f'{KaapanaApplicationOperator.HELM_API}/helm-install-chart'

        print('payload')
        print(payload)
        r = requests.post(url, json=payload)
        print(r)
        print(r.text)
        r.raise_for_status()

        t_end = time.time() + KaapanaApplicationOperator.TIMEOUT
        while time.time() < t_end:
            time.sleep(15)
            url = f'{KaapanaApplicationOperator.HELM_API}/view-chart-status'
            r = requests.get(url, params={'release_name': release_name})
            if r.status_code == 500 or r.status_code == 404:
                print(f'Release {release_name} was uninstalled. My job is done here!')
                break
            r.raise_for_status()

    @staticmethod
    def uninstall_helm_chart(kwargs):
        release_name = KaapanaApplicationOperator._get_release_name(kwargs)
        url = f'{KaapanaApplicationOperator.HELM_API}/helm-uninstall-chart'
        r = requests.get(url, params={'release_name': release_name})
        r.raise_for_status()
        print(r)
        print(r.text)

    @staticmethod
    def on_failure(info_dict):
        print("##################################################### ON FAILURE!")
        KaapanaApplicationOperator.uninstall_helm_chart(info_dict)

    @staticmethod
    def on_retry(info_dict):
        print("##################################################### ON RETRY!")
        KaapanaApplicationOperator.uninstall_helm_chart(info_dict)


    def __init__(self,
                 dag,
                 chart_name,
                 version,
                 name="helm-chart",
                 data_dir=None,
                 sets=None,
                 release_name=None,
                 **kwargs):

        self.chart_name = chart_name
        self.version = version
        self.sets = sets or dict()
        self.data_dir = data_dir or os.getenv('DATADIR', "")
        self.release_name=release_name

        super().__init__(
            dag=dag,
            name=name,
            python_callable=self.start,
            execution_timeout=timedelta(seconds=KaapanaApplicationOperator.TIMEOUT),
            **kwargs
        )