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
import tempfile

from sagemaker.deserializers import NumpyDeserializer
from sagemaker.predictor import Predictor
from sagemaker.serializers import NumpySerializer
from sm_ops import create_sm_args_parser, sm_data_prep, sm_deploy, sm_train, sm_validate

COMM_PATH = os.getenv("COMM_PATH", tempfile.mkdtemp())
os.makedirs(COMM_PATH, exist_ok=True)


def read_message(name):
    with open(os.path.join(COMM_PATH, name)) as f:
        lines = f.readlines()
    return [x.strip() for x in lines]


def forward_message(name, lines):
    if not isinstance(lines, list):
        lines = [lines]
    lines = '\n'.join(lines) + '\n'
    with open(os.path.join(COMM_PATH, name), 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    choices = ['data_prep', 'train', 'deploy', 'validate', 'all']
    parser = create_sm_args_parser()
    parser.add_argument("--action", choices=choices, default='all')
    args = parser.parse_args()
    steps = [args.action]
    if args.action == 'all':
        steps = choices[:-1]
    for step in steps:
        if step == 'data_prep':
            train, test = sm_data_prep(args.input_uri, args.output_uri_base)
            forward_message('data_prep', [train, test])
        elif step == 'train':
            lines = read_message('data_prep')
            train, test = lines[0], lines[1]
            artifact = sm_train(
                train,
                test,
                base_job_name=args.base_job_name,
                instance_type=args.train_instance_type,
                n_jobs=args.n_jobs,
            )
            forward_message('train', artifact)
        elif step == 'deploy':
            artifact = read_message('train')[0]
            predictor = sm_deploy(
                artifact=artifact, model_name=args.model_name, instance_type=args.deploy_instance_type
            )
            forward_message('deploy', predictor.endpoint)
        else:
            endpoint = read_message('deploy')[0]
            train, test = read_message('data_prep')
            predictor = Predictor(
                endpoint_name=endpoint, serializer=NumpySerializer(), deserializer=NumpyDeserializer()
            )
            result = sm_validate(predictor, test)
            print(f"avg abs error:{result}")
