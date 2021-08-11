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

import inspect
import logging
import re

from airflow.models import BaseOperator
from jinja2 import Environment

from liminal.runners.airflow.config import standalone_variable_backend

_VAR_REGEX = '(.*){{([^}]*)}}(.*)'

_BASE_OPERATOR_ATTRIBUTES = list(inspect.signature(BaseOperator.__init__).parameters.keys())


class OperatorWithVariableResolving(BaseOperator):
    """
    Operator delegator that handles liminal variable substitution at run time
    """

    def __init__(self,
                 dag,
                 task_config: dict,
                 variables: dict = None,
                 liminal_task_instance=None,
                 **kwargs):
        self.operator_delegate: BaseOperator = kwargs.pop('operator')
        self.liminal_task_instance = \
            liminal_task_instance.serialize() if liminal_task_instance else None
        if variables:
            self.variables = variables.copy()
        else:
            self.variables = {}
        self.task_config = task_config
        super().__init__(
            task_id=self.operator_delegate.task_id,
            dag=dag
        )
        self._LOG = logging.getLogger(self.__class__.__name__)

    def execute(self, context):
        attributes = self._get_operator_delegate_attributes()
        self.operator_delegate.template_fields = set(list(self.operator_delegate.template_fields) +
                                                     attributes)
        self.operator_delegate.render_template_fields(context,
                                                      LiminalEnvironment(self.variables,
                                                                         self.task_config))
        self.operator_delegate.render_template_fields(context)

        if 'ti' in context:
            context['ti'].xcom_push(key="liminal_task_instance", value=self.liminal_task_instance)

        return self.operator_delegate.execute(context)

    def post_execute(self, context, result=None):
        self.operator_delegate.post_execute(context, result)

    def _get_operator_delegate_attributes(self):
        return [
            attr for attr in dir(self.operator_delegate) if
            attr not in _BASE_OPERATOR_ATTRIBUTES and attr not in dir(BaseOperator)
            and not attr.startswith('_')
            and attr not in ('args', 'kwargs', 'lineage_data', 'subdag')
        ]


class LiminalEnvironment(Environment):
    def __init__(self, variables, task_config=None):
        super().__init__()
        self.val = None
        self.variables = variables.copy()
        logging.info(f'variables: {variables}')
        if task_config and 'variables' in task_config:
            task_variables = task_config['variables']
            if isinstance(task_variables, dict):
                self.variables.update(task_variables)
            elif isinstance(task_variables, str):
                variables_key = self.from_string(task_variables).render()
                if variables_key in variables:
                    self.variables.update(variables[variables_key])

    def from_string(self, val, **kwargs):
        self.val = val
        return self

    def render(self, *_, **kwargs):
        """
        Implements jinja2.environment.Template.render
        """
        conf = kwargs['dag_run'].conf if 'dag_run' in kwargs else {}
        return self.__render(self.val, conf, set())

    def __render(self, val: str, dag_run_conf: dict, unresolved_tags: set):
        token = re.match(_VAR_REGEX, val)
        if token and token[2].strip() not in unresolved_tags:
            tag_name = token[2].strip()
            prefix = self.__render(token[1], dag_run_conf, unresolved_tags)
            suffix = self.__render(token[3], dag_run_conf, unresolved_tags)
            if dag_run_conf and tag_name in dag_run_conf:
                return self.__render(prefix + str(dag_run_conf[tag_name]) + suffix,
                                     dag_run_conf,
                                     unresolved_tags)
            elif tag_name in self.variables:
                return self.__render(prefix + str(self.variables[tag_name]) + suffix,
                                     dag_run_conf,
                                     unresolved_tags)
            else:
                backend_value = standalone_variable_backend.get_variable(tag_name, None)
                if backend_value:
                    return self.__render(
                        prefix + backend_value + suffix,
                        dag_run_conf,
                        unresolved_tags
                    )
                else:
                    unresolved_tags.add(tag_name)
                    return self.__render(
                        prefix + '{{' + token[2] + '}}' + suffix,
                        dag_run_conf,
                        unresolved_tags
                    )
        else:
            return val


def add_variables_to_operator(operator, task) -> BaseOperator:
    """
    :param operator: Airflow operator
    :type operator: BaseOperator
    :param task: Task instance
    :type task: Task
    :returns: OperatorWithVariableResolving wrapping given operator
    """
    return OperatorWithVariableResolving(
        dag=task.dag,
        task_config=task.task_config,
        variables=task.variables,
        liminal_task_instance=task,
        operator=operator
    )
