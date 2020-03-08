from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
import json
import traceback
from airflow.models import DAG, TaskInstance
from airflow.utils import timezone
from random import randint


def split_list(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


class ConfigureParallelExecutionOperator(KubernetesPodOperator):

    def __init__(self,
                 config_type=None,
                 config_path=None,
                 executors=1,
                 *args,
                 **kwargs):
        namespace = kwargs['namespace']
        image = kwargs['image']
        name = kwargs['name']

        del kwargs['namespace']
        del kwargs['image']
        del kwargs['name']

        super().__init__(
            namespace=namespace,
            image=image,
            name=name,
            *args,
            **kwargs)
        self.config_type = config_type
        self.config_path = config_path
        self.executors = executors

    def execute(self, context):
        config_dict = {}

        self.log.info(f'config type: {self.config_type}')

        if self.config_type:
            if self.config_type == 'file':
                config_dict = {}  # future feature: return config from file
            elif self.config_type == 'sql':
                config_dict = {}  # future feature: return from sql config
            elif self.config_type == 'task':
                ti = context['task_instance']
                self.log.info(self.config_path)
                config_dict = ti.xcom_pull(task_ids=self.config_path)
            elif self.config_type == 'static':
                config_dict = json.loads(self.config_path)
            else:
                raise ValueError(f'Unknown config type: {self.config_type}')

        run_id = context['dag_run'].run_id

        return_conf = {'config_type': self.config_type,
                       'splits': {'0': {'run_id': run_id, 'configs': []}}}

        if config_dict:
            self.log.info(f'configs dict: {config_dict}')

            configs = config_dict['configs']

            self.log.info(f'configs: {configs}')

            config_splits = split_list(configs, self.executors)

            for i in range(self.executors):
                return_conf['splits'][str(i)] = {'run_id': run_id, 'configs': config_splits[i]}

        return return_conf

    def run_pod(self, context):
        return super().execute(context)


class ConfigurableKubernetesPodOperator(KubernetesPodOperator):

    def __init__(self,
                 config_task_id,
                 task_split,
                 *args,
                 **kwargs):
        namespace = kwargs['namespace']
        image = kwargs['image']
        name = kwargs['name']

        del kwargs['namespace']
        del kwargs['image']
        del kwargs['name']

        super().__init__(
            namespace=namespace,
            image=image,
            name=name,
            *args,
            **kwargs)

        self.config_task_id = config_task_id
        self.task_split = task_split

    def execute(self, context):
        if self.config_task_id:
            ti = context['task_instance']

            config = ti.xcom_pull(task_ids=self.config_task_id)

            if config:
                split = {}

                if 'configs' in config:
                    split = configs
                else:
                    split = config['splits'][str(self.task_split)]

                self.log.info(split)

                if split and split['configs']:
                    self.env_vars.update({'DATA_PIPELINE_CONFIG': json.dumps(split)})
                    return super().execute(context)
                else:
                    self.log.info(
                        f'Empty split config for split {self.task_split}. split config: {split}. config: {config}')
            else:
                raise ValueError('Config not found in task: ' + self.config_task_id)
        else:
            self.env_vars.update({'DATA_PIPELINE_CONFIG': '{}'})
            return super().execute(context)
