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
import pkgutil


def find_subclasses_in_packages(packages, parent_class):
    """
    Finds all subclasses of given parent class within given packages
    :return: map of module ref -> class
    """
    module_content = {}
    for p in packages:
        module_content.update(import_module(p))

    subclasses = set()
    work = [parent_class]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                work.append(child)
                # verify that the found class is in the relevant module
                for p in packages:
                    if p in child.__module__:
                        subclasses.add(child)
                        break

    return {sc.__module__.split(".")[-1]: sc for sc in subclasses}


def import_module(package, recursive=True):
    """
    Import all submodules of a module

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]

    :param recursive: search recursively (default: True)
    :type recursive: bool
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if not name == 'liminal_python_server':
            full_name = package.__name__ + '.' + name
            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(import_module(full_name))
    return results


def __get_class(the_module, the_class):
    m = __import__(the_module)
    for comp in the_module.split('.')[1:] + [the_class]:
        m = getattr(m, comp)
    return m
