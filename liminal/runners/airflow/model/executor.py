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

from abc import ABC, abstractmethod

from airflow.models import BaseOperator

from liminal.runners.airflow.operators.operator_with_variable_resolving import \
    OperatorWithVariableResolving


def add_variables_to_operator(operator, task) -> BaseOperator:
    """
    :param operator: Airflow operator
    :type operator: BaseOperator
    :param task: Task instance
    :returns: OperatorWithVariableResolving wrapping given operator
    """
    return OperatorWithVariableResolving(
        dag=task.dag,
        task_config=task.task_config,
        variables=task.variables,
        liminal_task_instance=task,
        operator=operator
    )


class Executor(ABC):
    """
    Executor Task.
    """
    # list of task types supported by the executor
    supported_task_types = []

    def __init__(self, executor_id, liminal_config, executor_config):
        self.liminal_config = liminal_config
        self.executor_id = executor_id
        self.executor_config = executor_config

    def apply_task_to_dag(self, **kwargs):
        task = kwargs['task']

        self._validate_task_type(task)

        return self._apply_executor_task_to_dag(task=task)

    @abstractmethod
    def _apply_executor_task_to_dag(self, **kwargs):
        pass

    def _validate_task_type(self, task):
        assert any([isinstance(task, tYp) for tYp in self.supported_task_types]), \
            f'supported task types: {self.supported_task_types}'
