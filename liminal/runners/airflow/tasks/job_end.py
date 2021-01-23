# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from liminal.runners.airflow.operators.job_status_operator import JobEndOperator
from liminal.runners.airflow.tasks.defaults.job_phase_task import JobPhaseTask


class JobEndTask(JobPhaseTask):
    """
      Job end task. Reports job end metrics.
    """

    def __init__(self, dag, liminal_config, pipeline_config, task_config, parent, trigger_rule):
        super().__init__(dag, liminal_config, pipeline_config, task_config, parent, trigger_rule)

    def apply_task_to_dag(self):
        job_end_task = JobEndOperator(
            task_id='end',
            namespace=self.metrics_namespace,
            application_name=self.pipeline_config['pipeline'],
            backends=self.metrics_backends,
            dag=self.dag,
            trigger_rule=self.trigger_rule
        )

        if self.parent:
            self.parent.set_downstream(job_end_task)

        return job_end_task
