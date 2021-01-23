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


def apply_variable_substitution(subliminal, superliminal):
    """
     Replace all {{variable.key}} in subliminal with variable.value variable in
     subliminal.variables + superliminal.variables
     """
    keyword = "variables"
    merged_variables = dict_util.merge_dicts(subliminal.get(keyword, {}), superliminal.get(keyword, {}), True)
    return dict_util.replace_placeholders(subliminal, merged_variables)


def apply_service_defaults(subliminal, superliminal):
    """ Apply defaults services
        :param subliminal: subliminal config
        :param superliminal: superliminal config
        :returns: enriched services with superliminal.service_defaults and subliminal.service_defaults
    """
    keyword = "service_defaults"
    superliminal_service_defaults = superliminal.get(keyword, {})
    subliminal_service_defaults = subliminal.get(keyword, {})

    merged_service_defaults = merge_dicts(subliminal_service_defaults, superliminal_service_defaults,
                                          recursive=True)

    return [merge_dicts(service, merged_service_defaults, True) for service in subliminal.get(__SERVICES, {})]


def apply_pipeline_defaults(subliminal, superliminal, pipeline):
    """Apply defaults values on given pipeline
    :param subliminal: subliminal config
    :param superliminal: superliminal config
    :param  pipeline: to apply defaults on

    :returns: pipeline after enrichment with superliminal.pipeline_defaults and subliminal.pipeline_defaults
    """
    keyword = "pipeline_defaults"
    superliminal_pipe_defaults = superliminal.get(keyword, {}).copy()
    subliminal_pipe_defaults = subliminal.get(keyword, {}).copy()
    superliminal_tasks = superliminal_pipe_defaults.pop(__TASKS, [])
    merged_pipeline_defaults = merge_dicts(subliminal_pipe_defaults, superliminal_pipe_defaults, True)
    pipeline = merge_dicts(pipeline, merged_pipeline_defaults, True)

    return apply_task_defaults(subliminal, superliminal, pipeline, superliminal_tasks=superliminal_tasks)


def apply_task_defaults(subliminal, superliminal, pipeline, superliminal_tasks):
    """Apply defaults task values on given pipeline
           :param subliminal: subliminal config
           :param superliminal: superliminal config
           :param  pipeline: where 'tasks' list can be found it
           :param  superliminal_tasks: superliminal tasks list

           :returns: pipeline after enrich with superliminal.tasks and superliminal.task_defaults
            and subliminal.task_defaults
    """
    pipeline[__TASKS] = __apply_task_defaults(subliminal, superliminal, pipeline.get(__TASKS, []), superliminal_tasks)

    return pipeline


def __apply_task_defaults(subliminal,
                          superliminal,
                          subliminal_tasks,
                          superliminal_tasks):
    keyword = "task_defaults"
    subliminal_tasks_defaults = subliminal.get(keyword, {})
    superliminal_tasks_defaults = superliminal.get(keyword, {})
    merged_task_defaults = merge_dicts(subliminal_tasks_defaults, superliminal_tasks_defaults, recursive=True)

    return __enrich_tasks(subliminal_tasks, superliminal_tasks, merged_task_defaults)


def __enrich_tasks(sub_tasks, super_tasks, task_defaults):
    result = []
    subtasks_added = False
    for task in super_tasks:
        if task.get('type') in ['pipeline'] and sub_tasks:
            result.extend(sub_tasks)
            subtasks_added = True
        else:
            result.append(task)

    # in case 'pipeline' keyword is missing from super - add subtasks at the end
    if not subtasks_added:
        result.extend(sub_tasks)

    return [merge_dicts(task, task_defaults.get(task['type'], {}), recursive=True) for task in result]
