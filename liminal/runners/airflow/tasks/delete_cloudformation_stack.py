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

from liminal.runners.airflow.model import task


class DeleteCloudFormationStackTask(task.Task):
    """
    Deletes cloud_formation stack.
    """

    def __init__(self, task_id, dag, parent, trigger_rule, liminal_config, pipeline_config,
                 task_config, executor=None):
        super().__init__(task_id, dag, parent, trigger_rule, liminal_config, pipeline_config,
                         task_config, executor=executor)

    def apply_task_to_dag(self):
        pass
