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
import os

split_id = int(os.environ['LIMINAL_SPLIT_ID'])
num_splits = int(os.environ['LIMINAL_NUM_SPLITS'])

inputs_dir = f'/mnt/vol1/inputs/{split_id}'
outputs_dir = '/mnt/vol1/outputs/'

if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

print(f'Running write_outputs for split id {split_id} [NUM_SPLITS = {num_splits}]')

for filename in os.listdir(inputs_dir):
    with open(os.path.join(inputs_dir, filename)) as infile, \
            open(os.path.join(
                outputs_dir,
                filename.replace('input', 'output').replace('.json', '.txt')
            ), 'w') as outfile:
        print(f'Writing output file: {outfile.name}')
        data = json.loads(infile.read())
        outfile.write(data['mykey'])
