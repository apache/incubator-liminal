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


class PythonImage:

    def build(self, base_path, relative_source_path, tag):
        """
        TODO: pydoc

        :param base_path:
        :param relative_source_path:
        :param tag:
        :param extra_files:
        :return:
        """

        print(f'Building image {tag}')

        temp_dir = tempfile.mkdtemp()
        # Delete dir for shutil.copytree to work
        os.rmdir(temp_dir)

        self.__copy_source(os.path.join(base_path, relative_source_path), temp_dir)

        requirements_file_path = os.path.join(temp_dir, 'requirements.txt')
        if not os.path.exists(requirements_file_path):
            with open(requirements_file_path, 'w'):
                pass

        docker_files = [
            os.path.join(os.path.dirname(__file__), 'Dockerfile'),
            os.path.join(os.path.dirname(__file__), 'container-setup.sh'),
            os.path.join(os.path.dirname(__file__), 'container-teardown.sh')
        ]

        for file in docker_files:
            self.__copy_file(file, temp_dir)

        docker_client = docker.from_env()

        # TODO: log docker output
        docker_client.images.build(path=temp_dir, tag=tag)

        docker_client.close()

        print(temp_dir, os.listdir(temp_dir))

        shutil.rmtree(temp_dir)

    @staticmethod
    def __copy_source(source_path, destination_path):
        shutil.copytree(source_path, destination_path)

    @staticmethod
    def __copy_file(source_file_path, destination_file_path):
        shutil.copy2(source_file_path, destination_file_path)
