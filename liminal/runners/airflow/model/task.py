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
"""
Base task.
"""


class Task:
    """
    Task.
    """

    def __init__(self, dag, liminal_config, pipeline_config, task_config, parent, trigger_rule):
        self.dag = dag
        self.liminal_config = liminal_config
        self.pipeline_config = pipeline_config
        self.task_config = task_config
        self.parent = parent
        self.trigger_rule = trigger_rule

    def apply_task_to_dag(self):
        """
        Registers Airflow operator to parent task.
        """
        raise NotImplementedError()
