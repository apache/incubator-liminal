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

from liminal.build.python import BasePythonImageBuilder


class PythonServerImageBuilder(BasePythonImageBuilder):

    def __init__(self, config, base_path, relative_source_path, tag):
        super().__init__(config, base_path, relative_source_path, tag)

    @staticmethod
    def _dockerfile_path():
        return os.path.join(os.path.dirname(__file__), 'Dockerfile')

    @staticmethod
    def _additional_files_from_paths():
        return [
            os.path.join(os.path.dirname(__file__), 'liminal_python_server.py'),
            os.path.join(os.path.dirname(__file__), 'python_server_requirements.txt')
        ]

    def _additional_files_from_filename_content_pairs(self):
        return super()._additional_files_from_filename_content_pairs() + \
               [('service.yml', yaml.safe_dump(self.config))]
