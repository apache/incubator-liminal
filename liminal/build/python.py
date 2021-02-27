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

import git

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

        version_file_path = os.path.join(temp_dir, 'VERSION')
        if not os.path.exists(version_file_path):
            with open(version_file_path, 'w') as file:
                repo = git.Repo(search_parent_directories=True)
                file.write(repo.head.object.hexsha)

        super()._write_additional_files(temp_dir)

    @staticmethod
    def _additional_files_from_paths():
        python_dir = os.path.join(os.path.join(os.path.dirname(__file__), 'image'), 'python')
        return [
            os.path.join(python_dir, 'container-setup.sh'),
            os.path.join(python_dir, 'container-teardown.sh'),
        ]

    def _additional_files_from_filename_content_pairs(self):
        with open(self._dockerfile_path()) as original:
            data = original.read()

        data = self.__mount_pip_conf(data)

        return [('Dockerfile', data)]

    def __mount_pip_conf(self, data):
        new_data = data
        if self.__PIP_CONF in self.config:
            if os.getenv(self.USE_LEGACY_DOCKER_VERSION):
                if os.getenv("PIP_ENV") is not None:
                    new_data = new_data.replace('{{copy_pip_conf}}', 'COPY $PIP_ENV /etc/')
                else:
                    new_data = new_data.replace('{{copy_pip_conf}}',
                                                f'COPY {self.config[self.__PIP_CONF]} /etc/')
                new_data = new_data.replace('{{mount}} ', '')
            else:
                new_data = '# syntax = docker/dockerfile:1.0-experimental\n' + data
                new_data = new_data.replace('{{copy_pip_conf}}', '')
                new_data = new_data.replace('{{mount}}',
                                            '--mount=type=secret,id=pip_config,'
                                            'dst=/etc/pip.conf \\\n')
        else:
            new_data = new_data.replace('{{copy_pip_conf}}', '')
            new_data = new_data.replace('{{mount}} ', '')
        return new_data

    def _build_flags(self, temp_dir):
        if self.__PIP_CONF in self.config:
            pip_conf_path = self.config[self.__PIP_CONF]
            prefix = f'{temp_dir}/' if not pip_conf_path.startswith('/') else ''
            return f'--secret id=pip_config,src={prefix}{pip_conf_path}'
        else:
            return ''

    def _use_buildkit(self):
        if self.__PIP_CONF in self.config:
            return True
