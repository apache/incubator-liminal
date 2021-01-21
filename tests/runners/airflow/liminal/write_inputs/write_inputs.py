# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

inputs_dir = '/mnt/vol1/inputs/'

num_files = int(os.environ['NUM_FILES'])
num_splits = int(os.environ['NUM_SPLITS'])

# create input files - split by round robin
for i in range(0, num_files):
    split_id = i % num_splits
    split_dir = os.path.join(inputs_dir, str(split_id))

    if not os.path.exists(split_dir):
        os.makedirs(split_dir)

    filename = os.path.join(split_dir, f'input{i}.json')
    with open(filename, 'w') as f:
        print(f'Writing input file {filename}')
        f.write(json.dumps({'mykey': f'myval{i}'}))
