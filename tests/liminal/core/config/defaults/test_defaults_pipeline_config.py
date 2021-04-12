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


class TestDefaultsPipelineConfig(TestCase):
    def test_apply(self):
        pipeline = {
            "name": "mypipe",
            "param": "constant",
            "tasks": [
                {
                    "task": "middle_task",
                    "type": "python"
                }
            ]
        }

        subliminal = {
            "name": "my_subliminal_test",
            "pipelines": [
                {
                    "name": "mypipe",
                    "param": "constant",
                    "tasks": [
                        {
                            "task": "middle_task",
                            "type": "python",
                            "env_vars": {
                                "env1": "env1"
                            }
                        }
                    ]
                }
            ],
            "pipeline_defaults": {
                "param1": "param1_value"
            }
        }
        superliminal = {
            "pipeline_defaults": {
                "param2": "param2super_value",
                "param3": "param3super_value",
                "before_tasks": [
                    {
                        "task": "first_task",
                        "type": "python"
                    }],
                "after_tasks": [
                    {
                        "task": "end_task",
                        "type": "python"
                    }
                ]
            },
            "task_defaults": {
                "python": {
                    "default_task_super": "default_task_super_value",
                    "env_vars": {
                        "env1": "env1super",
                        "env2": "env2super"
                    }
                }
            }
        }
        expected = {
            "param": "constant",
            "param3": "param3super_value",
            "param2": "param2super_value",
            "tasks": [
                {
                    "type": "python",
                    "env_vars": {
                        "env1": "env1super",
                        "env2": "env2super"
                    },
                    "task": "first_task",
                    "default_task_super": "default_task_super_value"
                },
                {
                    "type": "python",
                    "env_vars": {
                        "env1": "env1super",
                        "env2": "env2super"
                    },
                    "task": "middle_task",
                    "default_task_super": "default_task_super_value"
                },
                {
                    "type": "python",
                    "env_vars": {
                        "env1": "env1super",
                        "env2": "env2super"
                    },
                    "task": "end_task",
                    "default_task_super": "default_task_super_value"
                }
            ],
            "name": "mypipe",
            "param1": "param1_value"
        }

        self.assertEqual(expected, default_configs.apply_pipeline_defaults(subliminal, superliminal,
                                                                           pipeline))
