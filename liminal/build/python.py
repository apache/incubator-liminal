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


class PythonImageVersions:
    """
    Handles the python versions for python images.
    """

    @property
    def default_version(self):
        return '3.7'

    @property
    def supported_versions(self):
        return '3.6', '3.7', '3.8', '3.9'

    def get_image_name(self, python_version):
        """
        :param python_version: The python version that would be installed in
            the docker image. For example '3.8', '3.8.1' etc.
        :type python_version: str
        :return: The name of the base (slim) python image
        :rtype: str
        """
        if not python_version:
            python_version = self.default_version
        else:
            python_version = str(python_version)
        if python_version[:3] not in self.supported_versions:
            raise ValueError(f'liminal supports the following python versions: '
                             f'{self.supported_versions} but {python_version} '
                             f'were passed')
        return f'python:{python_version}-slim'


class BasePythonImageBuilder(ImageBuilder):
    """
    Base class for building python images.
    """

    __PIP_CONF = 'pip_conf'
    __PYTHON_VERSION = 'python_version'

    def __init__(self, config, base_path, relative_source_path, tag,
                 base_image=PythonImageVersions()):
        super().__init__(config, base_path, relative_source_path, tag)
        self._base_image = base_image

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
        data = self.__add_python_base_version(data)

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

    def __add_python_base_version(self, data):
        python_version = self.config.get(self.__PYTHON_VERSION)
        base_image = self._base_image.get_image_name(python_version)
        return data.replace('{{python}}', base_image)

    def _build_flags(self):
        if self.__PIP_CONF in self.config:
            return f'--secret id=pip_config,src={self.config[self.__PIP_CONF]}'
        else:
            return ''

    def _use_buildkit(self):
        if self.__PIP_CONF in self.config:
            return True
