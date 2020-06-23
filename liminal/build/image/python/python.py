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

from liminal.build.python import BasePythonImageBuilder


class PythonImageBuilder(BasePythonImageBuilder):

    def __init__(self, config, base_path, relative_source_path, tag):
        super().__init__(config, base_path, relative_source_path, tag)

    @staticmethod
    def _dockerfile_path():
        return os.path.join(os.path.dirname(__file__), 'Dockerfile')

    def _additional_files_from_paths(self):
        return [
            os.path.join(os.path.dirname(__file__), 'container-setup.sh'),
            os.path.join(os.path.dirname(__file__), 'container-teardown.sh'),
        ]
