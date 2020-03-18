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

import importlib.util
import inspect
import os
import sys


def find_subclasses_in_packages(packages, parent_class):
    """
    Finds all subclasses of given parent class within given packages
    :return: map of module ref -> class
    """
    classes = {}

    for py_path in [a for a in sys.path]:
        for root, directories, files in os.walk(py_path):
            if any(package in root for package in packages):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.py') and '__pycache__' not in file_path:
                        spec = importlib.util.spec_from_file_location(file[:-3], file_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        for name, obj in inspect.getmembers(mod):
                            if inspect.isclass(obj) and not obj.__name__.endswith('Mixin'):
                                module_name = mod.__name__
                                class_name = obj.__name__
                                parent_module = root[len(py_path) + 1:].replace('/', '.')
                                module = parent_module.replace('airflow.dags.', '') + \
                                         '.' + module_name
                                clazz = __get_class(module, class_name)
                                if issubclass(clazz, parent_class):
                                    classes.update({module_name: clazz})
    return classes


def __get_class(the_module, the_class):
    m = __import__(the_module)
    for comp in the_module.split('.')[1:] + [the_class]:
        m = getattr(m, comp)
    return m
