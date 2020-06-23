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

from liminal.build.image_builder import ImageBuilder


class BasePythonImageBuilder(ImageBuilder):
    """
    Base class for building python images.
    """

    __PIP_CONF = 'pip_conf'

    def __init__(self, config, base_path, relative_source_path, tag):
        super().__init__(config, base_path, relative_source_path, tag)

    @staticmethod
    def _dockerfile_path():
        raise NotImplementedError()

    def _write_additional_files(self, temp_dir):
        requirements_file_path = os.path.join(temp_dir, 'requirements.txt')
        if not os.path.exists(requirements_file_path):
            with open(requirements_file_path, 'w'):
                pass

        super()._write_additional_files(temp_dir)

    def _additional_files_from_filename_content_pairs(self):
        with open(self._dockerfile_path()) as original:
            data = original.read()

        data = self.__mount_pip_conf(data)

        return [('Dockerfile', data)]

    def __mount_pip_conf(self, data):
        new_data = data

        if self.__PIP_CONF in self.config:
            new_data = '# syntax = docker/dockerfile:1.0-experimental\n' + data
            new_data = new_data.replace('{{mount}}',
                                        '--mount=type=secret,id=pip_config,dst=/etc/pip.conf \\\n')
        else:
            new_data = new_data.replace('{{mount}} ', '')

        return new_data

    def _build_flags(self):
        if self.__PIP_CONF in self.config:
            return f'--secret id=pip_config,src={self.config[self.__PIP_CONF]}'
        else:
            return ''

    def _use_buildkit(self):
        if self.__PIP_CONF in self.config:
            return True
