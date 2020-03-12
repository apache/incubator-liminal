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

from rainbow.core.util import files_util
from rainbow.build.python.python_image import PythonImage


def build_rainbows(path):
    """
    TODO: doc for build_rainbow
    """

    config_files = files_util.find_config_files(path)

    for config_file in config_files:
        print(f'Building artifacts for file: {config_file}')

        with open(config_file) as stream:
            config = yaml.safe_load(stream)

            for pipeline in config['pipelines']:
                for task in pipeline['tasks']:
                    task_type = task['type']
                    task_instance = get_build_class(task_type)()
                    task_instance.build(base_path=os.path.dirname(config_file),
                                        relative_source_path=task['source'],
                                        tag=task['image'])


build_classes = {
    'python': PythonImage
}


def get_build_class(task_type):
    return build_classes[task_type]
