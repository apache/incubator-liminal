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
import json
from abc import ABC

from airflow.models import BaseOperator

from liminal.runners.airflow.model import executor


class Task(ABC):
    """
    Task.
    """

    def __init__(
        self, task_id, dag, parent, trigger_rule, liminal_config, pipeline_config, task_config, variables=None
    ):
        self.liminal_config = liminal_config
        self.dag = dag
        self.pipeline_config = pipeline_config
        self.task_id = task_id
        self.parent = parent
        self.trigger_rule = trigger_rule
        self.task_config = task_config
        self.variables = variables

    def serialize(self) -> str:
        """
        :returns: JSON string representation of this task
        """
        data = {
            'task_id': self.task_id,
            'dag': None,
            'parent': self.parent,
            'trigger_rule': self.trigger_rule,
            'liminal_config': self.liminal_config,
            'pipeline_config': self.pipeline_config,
            'task_config': self.task_config,
            'variables': self.variables,
        }

        return json.dumps(data, default=str)

    def _add_variables_to_operator(self, operator) -> BaseOperator:
        """
        :param operator: Airflow operator
        :type operator: BaseOperator
        :returns: OperatorWithVariableResolving wrapping given operator
        """
        return executor.add_variables_to_operator(operator, self)
