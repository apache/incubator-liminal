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

import logging
import os
import shutil
import subprocess
import tempfile
import time


class ImageBuilder:
    """
    Builds an image from source code
    """

    __NO_CACHE = 'no_cache'

    def __init__(self, config, base_path, relative_source_path, tag):
        """
        :param config: task/service config
        :param base_path: directory containing liminal yml
        :param relative_source_path: source path relative to liminal yml
        :param tag: image tag
        """
        self.base_path = base_path
        self.relative_source_path = relative_source_path
        self.tag = tag
        self.config = config

    def build(self):
        """
        Builds source code into an image.
        """
        logging.info(f'[ ] Building image: {self.tag}')

        temp_dir = self.__temp_dir()

        self.__copy_source_code(temp_dir)
        self._write_additional_files(temp_dir)

        no_cache = ''
        if self.__NO_CACHE in self.config and self.config[self.__NO_CACHE]:
            no_cache = '--no-cache=true'

        docker = 'docker' if shutil.which('docker') is not None else '/usr/local/bin/docker'
        docker_build_command = f'{docker} build {no_cache} ' + f'--tag {self.tag} '

        docker_build_command += f'--progress=plain {self._build_flags()} '

        docker_build_command += f'{temp_dir}'

        if self._use_buildkit():
            docker_build_command = f'DOCKER_BUILDKIT=1 {docker_build_command}'

        logging.info(docker_build_command)

        try:
            build_start = time.time()
            build_process = subprocess.Popen(docker_build_command, shell=True, stdout=subprocess.PIPE)
            # Poll process.stdout to show stdout live
            logging.info('=' * 80)
            timeout = 960
            while time.time() < build_start + timeout:
                output = build_process.stdout.readline()
                if build_process.poll() is not None:
                    break
                if output:
                    logging.info(output.strip())
            logging.info('=' * 80)

        except subprocess.CalledProcessError as e:
            for line in str(e.output)[2:-3].split('\\n'):
                logging.info(line)
            raise e

        self.__remove_dir(temp_dir)

        logging.info(f'[X] Building image: {self.tag} (Success).')

        return build_process

    def __copy_source_code(self, temp_dir):
        self.__copy_dir(os.path.join(self.base_path, self.relative_source_path), temp_dir)

    def _write_additional_files(self, temp_dir):
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

    def _build_flags(self):
        """
        Additional build flags to add to docker build command.
        """
        return ''

    def _use_buildkit(self):
        """
        overwrite with True to use docker buildkit
        """
        return False
