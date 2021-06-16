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

import json
import logging
import os

# Needs to be fixed in the following Jira:
# https://issues.apache.org/jira/browse/LIMINAL-76
inputs_dir = f'/mnt/vol1/inputs/'
outputs_dir = '/mnt/vol1/outputs/'

if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

for directory in os.listdir(inputs_dir):
    logging.info(f'Running write_outputs for split id {directory}')
    inputs_dir_file = os.path.join(inputs_dir, directory)
    for filename in os.listdir(inputs_dir_file):
        with open(os.path.join(inputs_dir_file, filename)) as infile, \
                open(os.path.join(
                    outputs_dir,
                    filename.replace('input', 'output').replace('.json', '.txt')
                ), 'w') as outfile:
            logging.info(f'Writing output file: {outfile.name}')
            data = json.loads(infile.read())
            outfile.write(data['mykey'])
