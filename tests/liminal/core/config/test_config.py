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

import os
from unittest import TestCase, mock

from liminal.core.config.config import ConfigUtil


# noinspection PyUnresolvedReferences,DuplicatedCode
class TestHierarchicalConfig(TestCase):

    @mock.patch("liminal.core.util.files_util.load")
    def test_safe_load(self, find_config_files_mock):
        subliminal = {
            "name": "my_subliminal_test",
            "type": "sub",
            "super": "my_superliminal_test",
            "pipelines": [
                {"name": "mypipe1", "param": "constant"},
                {"name": "mypipe2", "param": "constant"}
            ],
            "pipeline_defaults": {
                "param1": "param1_value"
            },
            "task_defaults": {
                "job_start": {
                    "task_sub_def": "task_sub_def_value"
                }
            }
        }
        superliminal = {
            "name": "my_superliminal_test",
            "type": "super",
            "super": "super_superliminal",
            "pipeline_defaults": {
                "param2": "param2super_value",
                "param3": "param3super_value"
            },
            "task_defaults": {
                "job_start": {
                    "task_def1": "task_def1_value",
                    "task_def2": {
                        "task_def2_1": "task_def2_1_value",
                    }
                }
            }
        }
        super_superliminal = {
            "name": "super_superliminal",
            "type": "super",
            "pipeline_defaults": {
                "param2": "param2super_value",
                "param3": "param3hyper_value",
                "param4": "param4hyper_value"
            }
        }

        expected = [{'name': 'my_subliminal_test',
                     'pipeline_defaults': {'param1': 'param1_value'},
                     'pipelines': [{'description': 'add defaults parameters for all pipelines',
                                    'name': 'mypipe1',
                                    'param': 'constant',
                                    'param1': 'param1_value',
                                    'param2': 'param2super_value',
                                    'param3': 'param3super_value',
                                    'param4': 'param4hyper_value',
                                    'tasks': [{'task': 'start',
                                               'task_def1': 'task_def1_value',
                                               'task_def2': {'task_def2_1': 'task_def2_1_value'},
                                               'task_sub_def': 'task_sub_def_value',
                                               'type': 'job_start'},
                                              {'task': 'sub_tasks', 'type': 'pipeline'},
                                              {'task': 'end', 'type': 'job_end'}]},
                                   {'description': 'add defaults parameters for all pipelines',
                                    'name': 'mypipe2',
                                    'param': 'constant',
                                    'param1': 'param1_value',
                                    'param2': 'param2super_value',
                                    'param3': 'param3super_value',
                                    'param4': 'param4hyper_value',
                                    'tasks': [{'task': 'start',
                                               'task_def1': 'task_def1_value',
                                               'task_def2': {'task_def2_1': 'task_def2_1_value'},
                                               'task_sub_def': 'task_sub_def_value',
                                               'type': 'job_start'},
                                              {'task': 'sub_tasks', 'type': 'pipeline'},
                                              {'task': 'end', 'type': 'job_end'}]}],
                     'service_defaults': {'description': 'add defaults parameters for all '
                                                         'services'},
                     'services': [],
                     'super': 'my_superliminal_test',
                     'task_defaults': {'job_start': {'task_sub_def': 'task_sub_def_value'}},
                     'type': 'sub'}]

        find_config_files_mock.return_value = {
            "my_subliminal_test": subliminal,
            "my_superliminal_test": superliminal,
            "super_superliminal": super_superliminal
        }

        config_util = ConfigUtil("")

        self.assertEqual(expected, config_util.safe_load(is_render_variables=True))

        # validate cache
        self.assertEqual(expected, config_util.loaded_subliminals)

    @mock.patch("liminal.core.util.files_util.load")
    def test_get_config(self, find_config_files_mock):
        find_config_files_mock.return_value = {
            "my_subliminal_test": {
                "type": "sub"
            },
            "my_superliminal_test": {
                "type": "super"
            }
        }

        config_util = ConfigUtil("")

        self.assertEqual({"type": "sub"},
                         config_util._ConfigUtil__get_config("my_subliminal_test"))

        self.assertEqual({"type": "super"},
                         config_util._ConfigUtil__get_config("my_superliminal_test"))

    @mock.patch("liminal.core.util.files_util.load")
    def test_get_superliminal(self, find_config_files_mock):
        hyperliminal = {'name': 'hyperliminal',
                        'pipeline_defaults': {'description': 'add defaults parameters for all '
                                                             'pipelines',
                                              'tasks': [{'task': 'start', 'type': 'job_start'},
                                                        {'task': 'sub_tasks', 'type': 'pipeline'},
                                                        {'task': 'end', 'type': 'job_end'}]},
                        'service_defaults': {'description': 'add defaults parameters for all '
                                                            'services'},
                        'task_defaults': {'description': 'add defaults parameters for all tasks '
                                                         'separate by task type'},
                        'type': 'super'}
        subliminal = {
            "name": "subliminal_test",
            "type": "sub"
        }

        find_config_files_mock.return_value = {
            "subliminal_test": subliminal
        }

        config_util = ConfigUtil("")

        self.assertEqual(hyperliminal,
                         config_util._ConfigUtil__get_superliminal(subliminal))

        self.assertEqual({},
                         config_util._ConfigUtil__get_superliminal(hyperliminal))

        liminal = {
            "name": "subliminal_test",
            "type": "sub",
            "super": "my_superliminal"
        }

        with self.assertRaises(FileNotFoundError):
            config_util._ConfigUtil__get_superliminal(liminal)

    @mock.patch("liminal.core.util.files_util.load")
    def test_merge_superliminals(self, find_config_files_mock):
        superliminal = {
            "name": "my_superliminal_test",
            "type": "super",
            "super": "super_superliminal",
            "pipeline_defaults": {
                "tasks": [
                    {"task": "start-2", "type": "spark"},
                    {"task": "middle-2", "type": "pipeline"},
                    {"task": "end-2", "type": "spark"}
                ]
            },
            "task_defaults": {
                "task_def1": "task_def1_value"
            }
        }

        super_superliminal = {
            "name": "super_superliminal",
            "type": "super",
            "pipeline_defaults": {
                "tasks": [
                    {"task": "start-1", "type": "spark"},
                    {"task": "middle-1", "type": "pipeline"},
                    {"task": "end-1", "type": "spark"}
                ]
            }
        }

        config_util = ConfigUtil("")

        find_config_files_mock.return_value = {
            "super_superliminal": super_superliminal,
            "superliminal": superliminal
        }

        expected = {
            'name': 'my_superliminal_test',
            'super': 'super_superliminal',
            'pipeline_defaults': {
                'tasks': [
                    {'task': 'start-1', 'type': 'spark'},
                    {'task': 'start-2', 'type': 'spark'},
                    {'task': 'middle-2', 'type': 'pipeline'},
                    {'task': 'end-2', 'type': 'spark'},
                    {'task': 'end-1', 'type': 'spark'}
                ]
            },
            'task_defaults':
                {
                    'task_def1': 'task_def1_value'
                },
            'type': 'super'}

        self.assertEqual(expected, config_util._ConfigUtil__merge_superliminals(superliminal,
                                                                                super_superliminal))

    @mock.patch("liminal.core.util.files_util.load")
    @mock.patch.dict(os.environ, {'env': 'myenv', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_safe_load_with_variables(self, find_config_files_mock):
        subliminal = {
            "name": "my_subliminal_test",
            "type": "sub",
            "super": "my_superliminal_test",
            "variables": {
                "var": "simple case",
                "var-2": "-case",
                "var_2": "_case",
                "image": "prod image",
                "a": "{{env}}1",
                "b": "{{a}}2",
                "c": "{{a}}{{b}}2"
            },
            "pipelines": [
                {"name": "mypipe1", "param": "{{var}}"},
                {"name": "mypipe2", "param": "{{var-2   }}"}
            ],
            "pipeline_defaults": {
                "param1": "{{var-2}}"
            },
            "task_defaults": {
                "job_start": {
                    "task_def1:": "task_sub_def_value"
                }

            },
            "services": [
                {
                    "name": "my_python_server",
                    "type": "python_server",
                    "image": "{{image}}"
                },
                {
                    "name": "my_python_server_for_stg",
                    "type": "python_server",
                    "image": "{{default_image}}"
                }
            ]}

        superliminal = {
            "name": "my_superliminal_test",
            "type": "super",
            "variables": {
                "var-2": "override",
                "var3": "super_var",
                "default_image": "default_image_value",
                "image": "default_image_value"
            },
            "super": "super_superliminal",
            "pipeline_defaults": {
                "param2": "{{pipe-var}}",
                "param3": "param3super_value"
            },
            "task_defaults": {
                "pipeline": {
                    "path": "{{var-2}}",
                    "task_def1": "task_def1_value",
                    "task_def2": {
                        "task_def2_1": "task_def2_1_value",
                    }
                }
            }
        }
        super_superliminal = {
            "name": "super_superliminal",
            "type": "super",
            "variables": {
                "default_image": "def_default_image_value"
            },
            "pipeline_defaults": {
                "global_conf": "{{var3}}",
                "param2": "param2super_value",
                "param3": "param3hyper_value",
                "param4": "param4hyper_value"
            }
        }

        expected = [{'name': 'my_subliminal_test',
                     'pipeline_defaults': {'param1': '-case'},
                     'pipelines': [{'description': 'add defaults parameters for all pipelines',
                                    'global_conf': 'super_var',
                                    'name': 'mypipe1',
                                    'param': 'simple case',
                                    'param1': '-case',
                                    'param2': '{{pipe-var}}',
                                    'param3': 'param3super_value',
                                    'param4': 'param4hyper_value',
                                    'tasks': [{'task': 'start',
                                               'task_def1:': 'task_sub_def_value',
                                               'type': 'job_start'},
                                              {'path': '-case',
                                               'task': 'sub_tasks',
                                               'task_def1': 'task_def1_value',
                                               'task_def2': {'task_def2_1': 'task_def2_1_value'},
                                               'type': 'pipeline'},
                                              {'task': 'end', 'type': 'job_end'}]},
                                   {'description': 'add defaults parameters for all pipelines',
                                    'global_conf': 'super_var',
                                    'name': 'mypipe2',
                                    'param': '-case',
                                    'param1': '-case',
                                    'param2': '{{pipe-var}}',
                                    'param3': 'param3super_value',
                                    'param4': 'param4hyper_value',
                                    'tasks': [{'task': 'start',
                                               'task_def1:': 'task_sub_def_value',
                                               'type': 'job_start'},
                                              {'path': '-case',
                                               'task': 'sub_tasks',
                                               'task_def1': 'task_def1_value',
                                               'task_def2': {'task_def2_1': 'task_def2_1_value'},
                                               'type': 'pipeline'},
                                              {'task': 'end', 'type': 'job_end'}]}],
                     'service_defaults': {'description': 'add defaults parameters for all '
                                                         'services'},
                     'services': [{'description': 'add defaults parameters for all services',
                                   'image': 'prod image',
                                   'name': 'my_python_server',
                                   'type': 'python_server'},
                                  {'description': 'add defaults parameters for all services',
                                   'image': 'default_image_value',
                                   'name': 'my_python_server_for_stg',
                                   'type': 'python_server'}],
                     'super': 'my_superliminal_test',
                     'task_defaults': {'job_start': {'task_def1:': 'task_sub_def_value'}},
                     'type': 'sub',
                     'variables': {'a': 'myenv1',
                                   'b': 'myenv12',
                                   'c': 'myenv1myenv122',
                                   'image': 'prod image',
                                   'var': 'simple case',
                                   'var-2': '-case',
                                   'var_2': '_case'}}]

        find_config_files_mock.return_value = {
            "my_subliminal_test": subliminal,
            "my_superliminal_test": superliminal,
            "super_superliminal": super_superliminal
        }

        config_util = ConfigUtil("")

        self.assertEqual(expected, config_util.safe_load(is_render_variables=True))

        # validate cache
        self.assertEqual(expected, config_util.loaded_subliminals)

    @mock.patch('os.path.exists')
    @mock.patch("liminal.core.environment.get_airflow_home_dir")
    @mock.patch("liminal.core.util.files_util.load")
    def test_liminal_config_snapshot(self, find_config_files_mock,
                                     get_airflow_dir_mock, path_exists_mock):
        subliminal = {
            "name": "my_subliminal_test",
            "type": "sub",
            "variables": {
                "var": 1,
                "var-2": True
            },
            "pipelines": [
                {"name": "mypipe1", "param": "{{var}}"},
                {"name": "mypipe2", "param": "{{var-2   }}"}
            ]
        }

        expected = {'name': 'my_subliminal_test', 'type': 'sub',
                    'service_defaults': {'description': 'add defaults parameters for all services'},
                    'task_defaults': {'description': 'add defaults parameters for all tasks separate by task type'},
                    'pipeline_defaults': {'description': 'add defaults parameters for all pipelines',
                                          'tasks': [{'task': 'start', 'type': 'job_start'},
                                                    {'task': 'sub_tasks', 'type': 'pipeline'},
                                                    {'task': 'end', 'type': 'job_end'}]},
                    'variables': {'var': 1, 'var-2': True}, 'pipelines': [
                {'name': 'mypipe1', 'param': '1', 'description': 'add defaults parameters for all pipelines',
                 'tasks': [{'task': 'start', 'type': 'job_start'}, {'task': 'sub_tasks', 'type': 'pipeline'},
                           {'task': 'end', 'type': 'job_end'}]},
                {'name': 'mypipe2', 'param': 'True', 'description': 'add defaults parameters for all pipelines',
                 'tasks': [{'task': 'start', 'type': 'job_start'}, {'task': 'sub_tasks', 'type': 'pipeline'},
                           {'task': 'end', 'type': 'job_end'}]}], 'services': []}

        find_config_files_mock.return_value = {
            "my_subliminal_test": subliminal
        }

        get_airflow_dir_mock.return_value = "/tmp"
        path_exists_mock.return_value = True

        with mock.patch("builtins.open", mock.mock_open()) as m:
            with mock.patch("yaml.dump") as ydm:
                ConfigUtil("").safe_load(is_render_variables=True)
                m.assert_called_once_with(os.path.join('/tmp', '../liminal_config_files/my_subliminal_test.yml'), 'w')
                ydm.assert_called_once_with(expected, m.return_value, default_flow_style=False)
