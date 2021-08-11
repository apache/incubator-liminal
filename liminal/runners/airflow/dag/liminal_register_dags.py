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
import logging
import os
import traceback
from datetime import datetime, timedelta

from airflow import DAG

from liminal.core.config.config import ConfigUtil
from liminal.core.util import class_util
from liminal.runners.airflow.executors import airflow
from liminal.runners.airflow.model import executor as liminal_executor
from liminal.runners.airflow.model.task import Task

__DEPENDS_ON_PAST = 'depends_on_past'


# noinspection PyBroadException
def register_dags(configs_path):
    """
    Registers pipelines in liminal yml files found in given path (recursively) as airflow DAGs.
    """
    logging.info(f'Registering DAGs from path: {configs_path}')
    config_util = ConfigUtil(configs_path)
    configs = config_util.safe_load(is_render_variables=False)

    if os.getenv('POD_NAMESPACE') != "jenkins":
        config_util.snapshot_final_liminal_configs()

    dags = []
    logging.info(f'found {len(configs)} liminal configs in path: {configs_path}')
    for config in configs:
        name = config['name'] if 'name' in config else None
        try:
            if not name:
                raise ValueError('liminal.yml missing field `name`')

            logging.info(f"Registering DAGs for {name}")

            owner = config.get('owner')

            trigger_rule = 'all_success'
            if 'always_run' in config and config['always_run']:
                trigger_rule = 'all_done'

            executors = __initialize_executors(config)

            default_executor = airflow.AirflowExecutor("default_executor", liminal_config=config,
                                                       executor_config={})

            for pipeline in config['pipelines']:
                default_args = __default_args(pipeline)
                dag = __initialize_dag(default_args, pipeline, owner)

                parent = None

                for task in pipeline['tasks']:
                    task_type = task['type']
                    task_instance = get_task_class(task_type)(
                        task_id=task['task'],
                        dag=dag,
                        parent=parent,
                        trigger_rule=trigger_rule,
                        liminal_config=config,
                        pipeline_config=pipeline,
                        task_config=task,
                        variables=config.get('variables', {})
                    )

                    executor_id = task.get('executor')
                    if executor_id:
                        executor = executors[executor_id]
                    else:
                        logging.info(f"Did not find `executor` in ${task['task']} config."
                                     f" Using the default executor (${type(default_executor)})"
                                     f" instead.")
                        executor = default_executor

                    parent = executor.apply_task_to_dag(task=task_instance)

                logging.info(f'registered DAG {dag.dag_id}: {dag.tasks}')

                dags.append((pipeline['pipeline'], dag))

        except Exception:
            logging.error(f'Failed to register DAGs for {name}')
            traceback.print_exc()

    return dags


def __initialize_executors(liminal_config):
    executors = {}
    for executor_config in liminal_config.get('executors', {}):
        executors[executor_config['executor']] = get_executor_class(executor_config['type'])(
            executor_config['executor'],
            liminal_config,
            executor_config
        )
    return executors


def __initialize_dag(default_args, pipeline, owner):
    pipeline_name = pipeline['pipeline']

    schedule_interval = default_args.get('schedule_interval', None)
    if not schedule_interval:
        schedule_interval = default_args.get('schedule', None)

    if owner and 'owner' not in default_args:
        default_args['owner'] = owner

    start_date = pipeline.get('start_date', datetime.min.time())
    if not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())

    default_args.pop('tasks', None)
    default_args.pop('schedule', None)
    default_args.pop('monitoring', None)
    default_args.pop('schedule_interval', None)

    dag = DAG(
        dag_id=pipeline_name,
        default_args=default_args,
        dagrun_timeout=timedelta(minutes=pipeline['timeout_minutes']),
        start_date=start_date,
        schedule_interval=schedule_interval,
        catchup=False
    )

    return dag


def __default_args(pipeline):
    default_args = {k: v for k, v in pipeline.items()}
    override_args = {
        'start_date': datetime.combine(pipeline['start_date'], datetime.min.time()),
        __DEPENDS_ON_PAST: default_args[
            __DEPENDS_ON_PAST
        ] if __DEPENDS_ON_PAST in default_args else False,
    }
    default_args.update(override_args)
    return default_args


logging.info(f'Loading task implementations..')

# TODO: add configuration for user tasks package
impl_packages = 'liminal.runners.airflow.tasks'
user_task_package = 'TODO: user_tasks_package'

tasks_by_liminal_name = class_util.find_subclasses_in_packages([impl_packages], Task)

logging.info(f'Finished loading task implementations: {tasks_by_liminal_name.keys()}')

executors_by_liminal_name = class_util.find_subclasses_in_packages(
    ['liminal.runners.airflow.executors'],
    liminal_executor.Executor)

logging.info(f'Finished loading executor implementations: {executors_by_liminal_name.keys()}')


def get_task_class(task_type):
    return tasks_by_liminal_name[task_type]


def get_executor_class(executor_type):
    return executors_by_liminal_name[executor_type]
