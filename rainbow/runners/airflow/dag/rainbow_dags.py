#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from datetime import datetime, timedelta
from os import environ

import yaml
from airflow import DAG
from airflow.models import Variable

from rainbow.core import environment
from rainbow.core.util import class_util
from rainbow.core.util import files_util
from rainbow.runners.airflow.model.task import Task
from rainbow.runners.airflow.tasks.defaults.job_end import JobEndTask
from rainbow.runners.airflow.tasks.defaults.job_start import JobStartTask

__DEPENDS_ON_PAST = 'depends_on_past'


def register_dags(configs_path):
    """
    TODO: doc for register_dags
    """
    print(f'Registering DAG from path: {configs_path}')
    config_files = files_util.find_config_files(configs_path)

    dags = []
    print(f'found {len(config_files)} in path: {configs_path}')
    for config_file in config_files:
        print(f'Registering DAG for file: {config_file}')

        with open(config_file) as stream:
            config = yaml.safe_load(stream)

            for pipeline in config['pipelines']:
                pipeline_name = pipeline['pipeline']

                default_args = {k: v for k, v in pipeline.items()}

                override_args = {
                    'start_date': datetime.combine(pipeline['start_date'], datetime.min.time()),
                    __DEPENDS_ON_PAST: default_args[__DEPENDS_ON_PAST] if __DEPENDS_ON_PAST in default_args else False,
                }

                default_args.update(override_args)

                dag = DAG(
                    dag_id=pipeline_name,
                    default_args=default_args,
                    dagrun_timeout=timedelta(minutes=pipeline['timeout_minutes']),
                    catchup=False
                )

                job_start_task = JobStartTask(dag, pipeline_name, None, pipeline, 'all_success')
                parent = job_start_task.apply_task_to_dag()

                trigger_rule = 'all_success'
                if 'always_run' in config and config['always_run']:
                    trigger_rule = 'all_done'

                for task in pipeline['tasks']:
                    task_type = task['type']
                    task_instance = get_task_class(task_type)(
                        dag, pipeline['pipeline'], parent if parent else None, task, trigger_rule
                    )

                    parent = task_instance.apply_task_to_dag()

                job_end_task = JobEndTask(dag, pipeline_name, parent, pipeline, 'all_done')
                job_end_task.apply_task_to_dag()

                print(f'registered DAG {dag.dag_id}: {dag.tasks}')

                globals()[pipeline_name] = dag
                dags.append(dag)

    return dags


print(f'Loading task implementations..')

# TODO: add configuration for user tasks package
impl_packages = 'rainbow.runners.airflow.tasks'
user_task_package = 'TODO: user_tasks_package'

task_classes = class_util.find_subclasses_in_packages([impl_packages], Task)


def tasks_by_rainbow_name(task_classes):
    return {full_name.replace(impl_packages, '').replace(clzz.__name__, '')[1:-1]: clzz
            for (full_name, clzz) in task_classes.items()}


tasks_by_rainbow_name = tasks_by_rainbow_name(task_classes)

print(f'Finished loading task implementations: {tasks_by_rainbow_name}')


def get_task_class(task_type):
    return tasks_by_rainbow_name[task_type]


register_dags(environment.get_dags_dir())
