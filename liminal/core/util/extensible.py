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
import sys

from liminal.build.image_builder import ImageBuilder
from liminal.core.util import class_util
from liminal.runners.airflow.model import executor
from liminal.runners.airflow.model.task import Task

__PLUGINS = 'plugins'


def __generate_extra_paths(plugin_type, extra_paths):
    return extra_paths or [] + (
        [f'{__PLUGINS}.{plugin_type}'] if f'{__PLUGINS}.{plugin_type}' in sys.path else [])


def load_executors(extra_paths=None):
    """
    Load all Executor extensions
    """
    package_paths = ['liminal.runners.airflow.executors'] + __generate_extra_paths('executors',
                                                                                   extra_paths)
    return class_util.find_subclasses_in_packages(package_paths, executor.Executor)


def load_tasks(extra_paths=None):
    """
    Load all Task extensions
    """
    package_paths = ['liminal.runners.airflow.tasks'] + __generate_extra_paths('tasks', extra_paths)
    return class_util.find_subclasses_in_packages(package_paths, Task)


def load_image_builders(extra_paths=None):
    """
    Load all ImageBuilder extensions
    """
    package_paths = ['liminal.build.image'] + __generate_extra_paths('images', extra_paths)
    return class_util.find_subclasses_in_packages(package_paths, ImageBuilder)
