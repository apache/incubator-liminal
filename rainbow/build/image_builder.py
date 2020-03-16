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
import shutil
import tempfile

import docker


class ImageBuilder:
    """
    Builds an image from source code
    """

    def __init__(self, config, base_path, relative_source_path, tag):
        """
        TODO: pydoc

        :param config:
        :param base_path:
        :param relative_source_path:
        :param tag:
        """
        self.base_path = base_path
        self.relative_source_path = relative_source_path
        self.tag = tag
        self.config = config

    def build(self):
        """
        Builds source code into an image.
        """
        print(f'[ ] Building image: {self.tag}')

        temp_dir = self.__temp_dir()

        self.__copy_source_code(temp_dir)
        self.__write_additional_files(temp_dir)

        # TODO: log docker output
        docker_client = docker.from_env()
        docker_client.images.build(path=temp_dir, tag=self.tag)
        docker_client.close()

        self.__remove_dir(temp_dir)

        print(f'[X] Building image: {self.tag} (Success).')

    def __copy_source_code(self, temp_dir):
        self.__copy_dir(os.path.join(self.base_path, self.relative_source_path), temp_dir)

    def __write_additional_files(self, temp_dir):
        # TODO: move requirements.txt related code to a parent class for python image builders.
        requirements_file_path = os.path.join(temp_dir, 'requirements.txt')
        if not os.path.exists(requirements_file_path):
            with open(requirements_file_path, 'w'):
                pass

        for file in [self._dockerfile_path()] + self._additional_files_from_paths():
            self.__copy_file(file, temp_dir)

        for filename, content in self._additional_files_from_filename_content_pairs():
            with open(os.path.join(temp_dir, filename), 'w') as file:
                file.write(content)

    def __temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        # Delete dir for shutil.copytree to work
        self.__remove_dir(temp_dir)
        return temp_dir

    @staticmethod
    def __remove_dir(temp_dir):
        shutil.rmtree(temp_dir)

    @staticmethod
    def __copy_dir(source_path, destination_path):
        shutil.copytree(source_path, destination_path)

    @staticmethod
    def __copy_file(source_file_path, destination_file_path):
        shutil.copy2(source_file_path, destination_file_path)

    @staticmethod
    def _dockerfile_path():
        """
        Path to Dockerfile
        """
        raise NotImplementedError()

    @staticmethod
    def _additional_files_from_paths():
        """
        List of paths to additional files
        """
        return []

    def _additional_files_from_filename_content_pairs(self):
        """
        File name and content pairs to create files from
        """
        return []
