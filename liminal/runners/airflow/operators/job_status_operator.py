# -*- coding: utf-8 -*-
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
from typing import Any

import pytz
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.exceptions import AirflowException
from airflow.lineage import apply_lineage
from airflow.models import BaseOperator
from airflow.utils.db import provide_session
from airflow.utils.decorators import apply_defaults
from airflow.utils.state import State


class JobStatusOperator(BaseOperator):
    """
    Base operator for job status operators.
    """
    template_ext = ()

    @apply_defaults
    def __init__(
            self,
            backends,
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backends = backends
        self.cloudwatch = None

    def execute(self, context):
        for backend in self.backends:
            if backend in self.report_functions:
                for metric in self.metrics(context):
                    self.report_functions[backend](self, metric)
            else:
                raise AirflowException('No such metrics backend: {}'.format(backend))

    def metrics(self, context):
        raise NotImplementedError

    def send_metric_to_cloudwatch(self, metric):
        self.get_cloudwatch().put_metric_data(metric)

    report_functions = {
        'cloudwatch': send_metric_to_cloudwatch
    }

    def get_cloudwatch(self):
        if not self.cloudwatch:
            self.cloudwatch = CloudWatchHook()
        return self.cloudwatch


class JobStartOperator(JobStatusOperator):
    ui_color = '#c5e5e8'

    def __init__(
            self,
            namespace,
            application_name,
            backends,
            *args, **kwargs):
        super().__init__(backends=backends, *args, **kwargs)
        self.namespace = namespace
        self.application_name = application_name

    def metrics(self, context):
        return [Metric(self.namespace, 'JobStarted', 1,
                       [Tag('ApplicationName', self.application_name)])]


class JobEndOperator(JobStatusOperator):
    ui_color = '#6d8fad'

    def __init__(
            self,
            namespace,
            application_name,
            backends,
            *args, **kwargs):
        super().__init__(backends=backends, *args, **kwargs)
        self.namespace = namespace
        self.application_name = application_name
        self.__job_result = 0

    def execute(self, context):
        self.__calculate_job_result(context)
        super().execute(context)
        
    def metrics(self, context):
        duration = round((pytz.utc.localize(datetime.utcnow()) - context['ti'].get_dagrun().start_date).total_seconds())

        self.log.info('Elapsed time: %s' % duration)

        self.log.info(f'dag final job result: {self.__job_result}')

        return [
            Metric(self.namespace, 'JobResult', self.__job_result, [Tag('ApplicationName', self.application_name)]),
            Metric(self.namespace, 'JobDuration', duration, [Tag('ApplicationName', self.application_name)])
        ]

    def __log_and_get_state(self, task_instance):
        state = task_instance.state

        self.log.info(f'Task {task_instance.task_id} finished with state = {state}')

        return state
    
    def __calculate_job_result(self, context):
        self.log.info('scanning task instances states.. ')
        task_instances = context['dag_run'].get_task_instances()
        task_states = [self.__log_and_get_state(task_instance)
                       for task_instance in task_instances
                       if task_instance.task_id != context['task_instance'].task_id]

        self.__job_result = 0
        if all((state == State.SUCCESS or state == State.SKIPPED) for state in task_states):
            self.__job_result = 1

    @apply_lineage
    @provide_session
    def post_execute(self, context: Any, result: Any = None, session=None):
        if self.__job_result == 0:
            self.log.info("Failing this DAG run due to task failure.")

            dag_run = context['ti'].get_dagrun()
            dag_run.end_date = datetime.utcnow()
            dag_run.state = State.FAILED

            session.merge(dag_run)


# noinspection PyAbstractClass
class CloudWatchHook(AwsHook):
    """
    Interact with AWS CloudWatch.
    """

    def __init__(self, region_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region_name = region_name
        self.conn = self.get_client_type('cloudwatch', self.region_name)

    def get_conn(self):
        return self.conn

    def put_metric_data(self, metric):
        value = metric.value

        cloudwatch = self.get_conn()

        dimensions = [{'Name': tag.name, 'Value': tag.value} for tag in metric.tags]

        cloudwatch.put_metric_data(
            Namespace=metric.namespace,
            MetricData=[
                {
                    'MetricName': metric.name,
                    'Dimensions': dimensions,
                    'Timestamp': datetime.utcnow(),
                    'Value': value,
                    'Unit': 'None'
                }
            ]
        )

        self.log.info(f'Published metric: {metric.name} with value: {value}')


class Metric:
    """
    Metric.
    :param namespace: namespace.
    :type name: str
    :param name: name.
    :type name: str
    :param value: value.
    :type value: float
    :param tags: list of tags.
    :type tags: List[str]
    """

    def __init__(
            self,
            namespace,
            name,
            value,
            tags):
        self.namespace = namespace
        self.name = name
        self.value = value
        self.tags = tags


class Tag:
    def __init__(
            self,
            name,
            value):
        self.name = name
        self.value = value
