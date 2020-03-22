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
from rainbow.runners.airflow.operators.job_status_operator import JobStartOperator
from rainbow.runners.airflow.tasks.defaults.default_task import DefaultTask


class JobStartTask(DefaultTask):
    """
    Job start task. Reports job start metrics.
    """

    def __init__(self, dag, pipeline_name, parent, config, trigger_rule):
        super().__init__(dag, pipeline_name, parent, config, trigger_rule)

    def apply_task_to_dag(self):
        job_start_task = JobStartOperator(
            task_id='start',
            namespace=self.metrics_namespace,
            application_name=self.pipeline_name,
            backends=self.metrics_backends,
            dag=self.dag,
            trigger_rule=self.trigger_rule
        )

        if self.parent:
            self.parent.set_downstream(job_start_task)

        return job_start_task
