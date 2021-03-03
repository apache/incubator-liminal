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

from unittest import TestCase

from liminal.core.config.defaults import default_configs


class TestDefaultsTaskConfig(TestCase):
    def test_apply(self):
        pipeline = {
            'pipeline': 'mypipe',
            "tasks": [
                {
                    "task": "middle",
                    "type": "spark",
                    "task_param": "task_middle_param"
                },
                {
                    "task": "end",
                    "type": "python",
                    "task_param": "task_end_param"
                }
            ]
        }

        subliminal = {'pipelines': [pipeline]}

        superliminal = {
            "task_defaults": {
                "python": {
                    "env_vars": {
                        "env2": "env2value"
                    }
                },
                "spark": {
                    "task_param": "task_spark_param",
                    "executor": "emr"
                }
            }
        }

        expected = {'pipeline': 'mypipe',
                    'tasks': [{'env_vars': {'env1': 'env1value', 'env2': 'env2value'},
                               'task': 'start',
                               'type': 'python'},
                              {'executor': 'emr',
                               'task': 'middle',
                               'task_param': 'task_middle_param',
                               'type': 'spark'},
                              {'env_vars': {'env2': 'env2value'},
                               'task': 'end',
                               'task_param': 'task_end_param',
                               'type': 'python'}]}
        self.assertEqual(expected, default_configs.apply_task_defaults(subliminal,
                                                                       superliminal,
                                                                       pipeline=pipeline,
                                                                       superliminal_tasks=[{
                                                                           "task": "start",
                                                                           "type": "python",
                                                                           "env_vars": {
                                                                               "env1": "env1value"
                                                                           }
                                                                       }]))

    def test_missing_tasks_from_supr(self):
        pipeline = {
            'pipeline': 'mypipe',
            "tasks": [
                {
                    "task": "middle",
                    "type": "spark",
                    "task_param": "task_middle_param"
                },
                {
                    "task": "end",
                    "type": "python",
                    "task_param": "task_end_param"
                }
            ]
        }

        subliminal = {'pipelines': [pipeline]}

        superliminal = {
            "task_defaults": {
                "python": {
                    "env_vars": {
                        "env2": "env2value"
                    }
                },
                "spark": {
                    "task_param": "task_spark_param"
                }
            }
        }

        expected = {'pipeline': 'mypipe',
                    'tasks': [{'task': 'middle',
                               'task_param': 'task_middle_param',
                               'type': 'spark'},
                              {'env_vars': {'env2': 'env2value'},
                               'task': 'end',
                               'task_param': 'task_end_param',
                               'type': 'python'}]}

        self.assertEqual(expected, default_configs.apply_task_defaults(subliminal,
                                                                       superliminal,
                                                                       pipeline=pipeline,
                                                                       superliminal_tasks=superliminal[
                                                                           'task_defaults'].get(
                                                                           'tasks', [])))

    def test_missing_tasks_from_sub(self):
        pipeline = {
            'pipeline': 'mypipe'
        }

        subliminal = {'pipelines': [pipeline]}

        superliminal = {
            "task_defaults": {
                "python": {
                    "env_vars": {
                        "env2": "env2value"
                    }
                },
                "spark": {
                    "task_param": "task_start_param",
                }
            },
            "pipeline_defaults": {
                "tasks": [
                    {
                        "task": "start",
                        "task_param": "task_middle_param",
                        "type": "spark"
                    },
                    {
                        "env_vars": {
                            "env2": "env2value"
                        },
                        "task": "end",
                        "task_param": "task_end_param",
                        "type": "pipeline"
                    }
                ]
            }
        }

        expected = {'pipeline': 'mypipe',
                    'tasks': [{
                        'task': 'start',
                        'task_param': 'task_middle_param',
                        'type': 'spark'},
                        {'env_vars': {'env2': 'env2value'},
                         'task': 'end',
                         'task_param': 'task_end_param',
                         'type': 'pipeline'}]}

        self.assertEqual(expected, default_configs.apply_task_defaults(subliminal,
                                                                       superliminal,
                                                                       pipeline=pipeline,
                                                                       superliminal_tasks=superliminal[
                                                                           'pipeline_defaults'].pop(
                                                                           'tasks', [])))
