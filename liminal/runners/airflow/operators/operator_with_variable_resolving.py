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
import re

from airflow.models import BaseOperator
from jinja2 import Environment

from liminal.runners.airflow.config import standalone_variable_backend

_VAR_REGEX = '(.*){{([^}]*)}}(.*)'


class OperatorWithVariableResolving(BaseOperator):
    """
    Operator delegator that handles liminal variable substitution at run time
    """

    def __init__(self,
                 liminal_config: dict,
                 *args,
                 **kwargs):
        self.operator_delegate: BaseOperator = kwargs.pop('operator')
        self.liminal_config = liminal_config
        super().__init__(
            *args,
            **kwargs)
        self._LOG = logging.getLogger(self.__class__.__name__)

    def execute(self, context):
        self.operator_delegate.render_template_fields(context,
                                                      LiminalEnvironment(self.liminal_config))
        self.operator_delegate.render_template_fields(context)
        return self.operator_delegate.execute(context)


class LiminalEnvironment(Environment):
    def __init__(self, config: dict):
        super().__init__()
        self.val = None
        self.variables = config.get('variables', {})

    def from_string(self, val, **kwargs):
        self.val = val
        return self

    def render(self, *_, **kwargs):
        """
        Implements jinja2.environment.Template.render
        """
        conf = kwargs['dag_run'].conf if 'dag_run' in kwargs else {}
        return self.__render(self.val, conf, set())

    def __render(self, val: str, dag_run_conf: dict, seen_tags: set):
        token = re.match(_VAR_REGEX, val)
        if token and token[2].strip() not in seen_tags:
            tag_name = token[2].strip()
            seen_tags.add(tag_name)
            prefix = self.__render(token[1], dag_run_conf, seen_tags)
            suffix = self.__render(token[3], dag_run_conf, seen_tags)
            if dag_run_conf and tag_name in dag_run_conf:
                return self.__render(prefix + str(dag_run_conf[tag_name]) + suffix,
                                     dag_run_conf,
                                     seen_tags)
            elif tag_name in self.variables:
                return self.__render(prefix + str(self.variables[tag_name]) + suffix,
                                     dag_run_conf,
                                     seen_tags)
            else:
                backend_value = standalone_variable_backend.get_variable(tag_name, None)
                if backend_value:
                    return self.__render(
                        prefix + backend_value + suffix,
                        dag_run_conf,
                        seen_tags
                    )
                else:
                    return self.__render(
                        prefix + '{{' + token[2] + '}}' + suffix,
                        dag_run_conf,
                        seen_tags
                    )
        else:
            return val
