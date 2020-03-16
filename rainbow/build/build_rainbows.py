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

import yaml

from rainbow.build.http.python.python_server_image import PythonServerImageBuilder
from rainbow.build.python.python_image import PythonImageBuilder
from rainbow.core.util import files_util


def build_rainbows(path):
    """
    TODO: doc for build_rainbows
    """
    config_files = files_util.find_config_files(path)

    for config_file in config_files:
        print(f'Building artifacts for file: {config_file}')

        base_path = os.path.dirname(config_file)

        with open(config_file) as stream:
            rainbow_config = yaml.safe_load(stream)

            for pipeline in rainbow_config['pipelines']:
                for task in pipeline['tasks']:
                    builder_class = __get_task_build_class(task['type'])
                    __build_image(base_path, task, builder_class)

                for service in rainbow_config['services']:
                    builder_class = __get_service_build_class(service['type'])
                    __build_image(base_path, service, builder_class)


def __build_image(base_path, builder_config, builder):
    if 'source' in builder_config:
        server_builder_instance = builder(
            config=builder_config,
            base_path=base_path,
            relative_source_path=builder_config['source'],
            tag=builder_config['image'])
        server_builder_instance.build()
    else:
        print(f"No source provided for {builder_config['name']}, skipping.")


__task_build_classes = {
    'python': PythonImageBuilder,
}

__service_build_classes = {
    'python_server': PythonServerImageBuilder
}


def __get_task_build_class(task_type):
    return __task_build_classes[task_type]


def __get_service_build_class(task_type):
    return __service_build_classes[task_type]
