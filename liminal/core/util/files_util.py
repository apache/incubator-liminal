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

import yaml

# { path -> { name -> config_file } }
cached_files = dict()
cached_source_files = dict()


def resolve_pipeline_source_file(config_name):
    """
    Return the source (file) path of the given config name
    """
    return cached_source_files[config_name]


def load(path):
    """
    :param path: config path
    :returns dict of {name -> loaded config file} from all liminal.y[a]ml files under given path
    """

    if cached_files.get(path):
        return cached_files[path]

    config_entities = {}

    for file_data in find_config_files(path):
        with open(file_data, 'r') as data:
            config_file = yaml.safe_load(data)
            config_entities[config_file['name']] = config_file
            cached_source_files[config_file['name']] = file_data

    cached_files[path] = config_entities
    return config_entities


def find_config_files(path):
    """
    :param path: config path
    :returns list of all liminal.y[a]ml files under config path
    """
    files = []
    logging.info(path)
    for r, d, f in os.walk(path):
        for file in f:
            if os.path.basename(file) in ['liminal.yml', 'liminal.yaml']:
                logging.info(os.path.join(r, file))
                files.append(os.path.join(r, file))
    return files
