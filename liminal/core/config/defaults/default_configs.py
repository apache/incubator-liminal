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

from liminal.core.util import dict_util
from liminal.core.util.dict_util import merge_dicts

__SERVICES = "services"
__TASKS = "tasks"
__BEFORE_TASKS = "before_tasks"
__AFTER_TASKS = "after_tasks"


def apply_variable_substitution(subliminal, superliminal, is_render_variables=False):
    """
    if is_render_variables is True
       Replace all {{variable.key}} in subliminal with variable.value variable in
       subliminal.variables + superliminal.variables
    else
       merge subliminal.variables with superliminal.variables without replace
       placeholders
    """
    keyword = "variables"
    merged_variables = dict_util.merge_dicts(subliminal.get(keyword, {}), superliminal.get(keyword, {}), True)
    if is_render_variables:
        for k, v in merged_variables.items():
            if isinstance(v, str) or (not isinstance(v, dict) and not isinstance(v, list)):
                merged_variables[k] = dict_util.replace_placholders_in_string(str(v), merged_variables)

        merged_variables = dict_util.replace_placeholders(merged_variables, merged_variables)
        return dict_util.replace_placeholders(subliminal, merged_variables)
    else:
        subliminal[keyword] = merged_variables
        return subliminal


def apply_service_defaults(subliminal, superliminal):
    """Apply defaults services
    :param subliminal: subliminal config
    :param superliminal: superliminal config
    :returns: enriched services with superliminal.service_defaults & subliminal.service_defaults
    """
    keyword = "service_defaults"
    superliminal_service_defaults = superliminal.get(keyword, {})
    subliminal_service_defaults = subliminal.get(keyword, {})

    merged_service_defaults = merge_dicts(subliminal_service_defaults, superliminal_service_defaults, recursive=True)

    return [merge_dicts(service, merged_service_defaults, True) for service in subliminal.get(__SERVICES, {})]


def apply_pipeline_defaults(subliminal, superliminal, pipeline):
    """Apply defaults values on given pipeline
    :param subliminal: subliminal config
    :param superliminal: superliminal config
    :param  pipeline: to apply defaults on

    :returns: enriched pipeline with superliminal.pipeline_defaults & subliminal.pipeline_defaults
    """
    keyword = "pipeline_defaults"
    superliminal_pipe_defaults = superliminal.get(keyword, {}).copy()
    subliminal_pipe_defaults = subliminal.get(keyword, {}).copy()
    superliminal_before_tasks = superliminal_pipe_defaults.pop(__BEFORE_TASKS, [])
    superliminal_after_tasks = superliminal_pipe_defaults.pop(__AFTER_TASKS, [])
    merged_pipeline_defaults = merge_dicts(subliminal_pipe_defaults, superliminal_pipe_defaults, True)
    pipeline = merge_dicts(pipeline, merged_pipeline_defaults, True)

    return apply_task_defaults(
        subliminal,
        superliminal,
        pipeline,
        superliminal_before_tasks=superliminal_before_tasks,
        superliminal_after_tasks=superliminal_after_tasks,
    )


def apply_task_defaults(subliminal, superliminal, pipeline, superliminal_before_tasks, superliminal_after_tasks):
    """Apply defaults task values on given pipeline
    :param subliminal: subliminal config
    :param superliminal: superliminal config
    :param  pipeline: where 'tasks' list can be found it
    :param  superliminal_before_tasks: superliminal before subtasks list
    :param  superliminal_after_tasks: superliminal after subtasks list

    :returns: pipeline after enrich with superliminal.tasks and superliminal.task_defaults
     and subliminal.task_defaults
    """
    pipeline[__TASKS] = __apply_task_defaults(
        subliminal, superliminal, pipeline.get(__TASKS, []), superliminal_before_tasks, superliminal_after_tasks
    )

    return pipeline


def __apply_task_defaults(
    subliminal, superliminal, subliminal_tasks, superliminal_before_tasks, superliminal_after_tasks
):
    keyword = "task_defaults"
    subliminal_tasks_defaults = subliminal.get(keyword, {})
    superliminal_tasks_defaults = superliminal.get(keyword, {})
    merged_task_defaults = merge_dicts(subliminal_tasks_defaults, superliminal_tasks_defaults, recursive=True)

    return __enrich_tasks(subliminal_tasks, superliminal_before_tasks, superliminal_after_tasks, merged_task_defaults)


def __enrich_tasks(sub_tasks, super_before_tasks, super_after_tasks, task_defaults):
    merged_tasks = super_before_tasks + sub_tasks + super_after_tasks

    return [merge_dicts(task, task_defaults.get(task.get('type', ''), {}), recursive=True) for task in merged_tasks]
