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

from datetime import datetime

import yaml
from airflow import DAG

from rainbow.core.util import files_util
from rainbow.runners.airflow.tasks.python import PythonTask


def register_dags(configs_path):
    """
    TODO: doc for register_dags
    """

    config_files = files_util.find_config_files(configs_path)

    dags = []

    for config_file in config_files:
        print(f'Registering DAG for file: f{config_file}')

        with open(config_file) as stream:
            # TODO: validate config
            config = yaml.safe_load(stream)

            for pipeline in config['pipelines']:
                parent = None

                default_args = {
                    'owner': config['owner'],
                    'start_date': datetime.combine(pipeline['start_date'], datetime.min.time())
                }
                # TODO: add all relevant airflow args
                dag = DAG(
                    dag_id='test_dag',
                    default_args=default_args
                )

                for task in pipeline['tasks']:
                    task_type = task['type']
                    task_instance = get_task_class(task_type)(
                        dag, pipeline['pipeline'], parent if parent else None, task, 'all_success'
                    )
                    parent = task_instance.apply_task_to_dag()

                    print(f'{parent}{{{task_type}}}')

                dags.append(dag)
    return dags


# TODO: task class registry
task_classes = {
    'python': PythonTask
}


def get_task_class(task_type):
    return task_classes[task_type]


if __name__ == '__main__':
    # TODO: configurable yaml dir
    path = 'tests/runners/airflow/dag/rainbow'
    register_dags(path)
