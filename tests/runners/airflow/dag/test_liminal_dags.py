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
import unittest
from unittest import TestCase, mock

from liminal.core.config.config import ConfigUtil
from liminal.runners.airflow.dag.liminal_dags import register_dags
from liminal.runners.airflow.operators.job_status_operator import JobEndOperator, JobStartOperator


class Test(TestCase):
    def test_register_dags(self):
        dags = self.get_register_dags()

        self.assertEqual(len(dags), 1)

        test_pipeline = dags[0]

        # TODO: elaborate tests to assert all dags have correct tasks
        self.assertEqual(test_pipeline.dag_id, 'my_pipeline')

    def test_default_start_task(self):
        dags = self.get_register_dags()

        task_dict = dags[0].task_dict

        self.assertIsInstance(task_dict['start'], JobStartOperator)

    def test_default_end_task(self):
        dags = self.get_register_dags()

        task_dict = dags[0].task_dict

        self.assertIsInstance(task_dict['end'], JobEndOperator)

    def test_default_args(self):
        dag = self.get_register_dags()[0]
        default_args = dag.default_args

        keys = default_args.keys()
        self.assertIn('default_arg_loaded', keys)
        self.assertIn('default_array_loaded', keys)
        self.assertIn('default_object_loaded', keys)

    @staticmethod
    @mock.patch.object(ConfigUtil, "snapshot_final_liminal_configs")
    def get_register_dags(mock_snapshot_final_liminal_configs):
        mock_snapshot_final_liminal_configs.side_effect = None
        base_path = os.path.join(os.path.dirname(__file__), '../../apps/test_app')
        return register_dags(base_path)


if __name__ == '__main__':
    unittest.main()
