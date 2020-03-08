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

import unittest

from rainbow.runners.airflow.compiler import rainbow_compiler


class TestRainbowCompiler(unittest.TestCase):

    def test_parse(self):
        expected = {'name': 'MyPipeline', 'owner': 'Bosco Albert Baracus', 'pipeline': {'timeout-minutes': 45, 'schedule': '0 * 1 * *', 'metrics-namespace': 'TestNamespace', 'tasks': [{'name': 'mytask1', 'type': 'sql', 'description': 'mytask1 is cool', 'query': 'select * from mytable', 'overrides': [{'prod': None, 'partition-columns': 'dt', 'output-table': 'test.test_impression_prod', 'output-path': 's3://mybucket/myproject-test/impression', 'emr-cluster-name': 'spark-playground-prod'}, {'stg': None, 'query': 'select * from mytable', 'partition-columns': 'dt', 'output-table': 'test.test_impression_stg', 'output-path': 's3://mybucket/haya-test/impression', 'emr-cluster-name': 'spark-playground-staging'}], 'tasks': [{'name': 'my_static_config_task', 'type': 'python', 'description': 'my 1st ds task', 'artifact-id': 'mytask1artifactid', 'source': 'mytask1folder', 'env-vars': {'env1': 'a', 'env2': 'b'}, 'config-type': 'static', 'config-path': '{"configs": [ { "campaign_id": 10 }, { "campaign_id": 20 } ]}', 'cmd': 'python -u my_app.py'}, {'task': None, 'name': 'my_no_config_task', 'type': 'python', 'description': 'my 2nd ds task', 'artifact-id': 'mytask1artifactid', 'env-vars': {'env1': 'a', 'env2': 'b'}, 'request-cpu': '100m', 'request-memory': '65M', 'cmd': 'python -u my_app.py foo bar'}, {'task': None, 'name': 'my_create_custom_config_task', 'type': 'python', 'description': 'my 2nd ds task', 'artifact-id': 'myconftask', 'source': 'myconftask', 'output-config-path': '/my_conf.json', 'env-vars': {'env1': 'a', 'env2': 'b'}, 'cmd': 'python -u my_app.py foo bar'}, {'task': None, 'name': 'my_custom_config_task', 'type': 'python', 'description': 'my 2nd ds task', 'artifact-id': 'mytask1artifactid', 'config-type': 'task', 'config-path': 'my_create_custom_config_task', 'env-vars': {'env1': 'a', 'env2': 'b'}, 'cmd': 'python -u my_app.py foo bar'}, {'task': None, 'name': 'my_parallelized_static_config_task', 'type': 'python', 'description': 'my 3rd ds task', 'artifact-id': 'mytask1artifactid', 'executors': 5, 'env-vars': {'env1': 'x', 'env2': 'y', 'myconf': '$CONFIG_FILE'}, 'config-type': 'static', 'config-path': '{"configs": [ { "campaign_id": 10 }, { "campaign_id": 20 }, { "campaign_id": 30 }, { "campaign_id": 40 }, { "campaign_id": 50 }, { "campaign_id": 60 }, { "campaign_id": 70 }, { "campaign_id": 80 } ]}', 'cmd': 'python -u my_app.py $CONFIG_FILE'}, {'task': None, 'name': 'my_parallelized_custom_config_task', 'type': 'python', 'description': 'my 4th ds task', 'artifact-id': 'mytask1artifactid', 'executors': 5, 'config-type': 'task', 'config-path': 'my_create_custom_config_task', 'cmd': 'python -u my_app.py'}, {'task': None, 'name': 'my_parallelized_no_config_task', 'type': 'python', 'description': 'my 4th ds task', 'artifact-id': 'mytask1artifactid', 'executors': 5, 'cmd': 'python -u my_app.py'}]}]}, 'services': [{'service': None, 'name': 'myserver1', 'type': 'python-server', 'description': 'my python server', 'artifact-id': 'myserver1artifactid', 'source': 'myserver1logicfolder', 'endpoints': [{'endpoint': None, 'path': '/myendpoint1', 'module': 'mymodule1', 'function': 'myfun1'}, {'endpoint': None, 'path': '/myendpoint2', 'module': 'mymodule2', 'function': 'myfun2'}]}]}
        actual = rainbow_compiler.parse_yaml('tests/runners/airflow/compiler/rainbow.yml')
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
