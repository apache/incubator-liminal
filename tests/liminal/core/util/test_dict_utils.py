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
from unittest import TestCase, mock

from liminal.core.util import dict_util


class TestDictUtils(TestCase):
    def setUp(self) -> None:
        self.dict1 = {"env": "env1", "env_dict": {"env3": "env3"}, "env4": "env4"}

        self.dict2 = {"env": "env1", "env_dict": {"env2": "env2"}}

    def test_merge_dicts(self):
        expected = {"env": "env1", "env4": "env4", "env_dict": {"env2": "env2"}}

        self.assertEqual(expected, dict_util.merge_dicts(self.dict1, self.dict2))

    def test_recursive_merge_dicts(self):
        expected = {"env": "env1", "env4": "env4", "env_dict": {"env2": "env2", "env3": "env3"}}
        self.assertEqual(expected, dict_util.merge_dicts(self.dict1, self.dict2, True))

    def test_merge_with_empty(self):
        self.assertEqual(self.dict2, dict_util.merge_dicts({}, self.dict2, True))
        self.assertEqual(self.dict2, dict_util.merge_dicts({}, self.dict2))

        self.assertEqual(self.dict2, dict_util.merge_dicts(self.dict2, {}, True))
        self.assertEqual(self.dict2, dict_util.merge_dicts(self.dict2, {}))

    def test_replace_variables_simple_case(self):
        dct = {
            "env": "{{env_var}}",
            "env_dict": {"env3": "{{ var1 }}"},
            "env4": "{{var2 }}",
            "env5": "{{{var2}}",
            "env6": "{{var3}}",
        }

        variables = {"env_var": "env value", "var1": "value1", "var2": "value2"}

        expected = {
            "env": "env value",
            "env_dict": {"env3": "value1"},
            "env4": "value2",
            "env5": "{value2",
            "env6": "{{var3}}",
        }

        self.assertEqual(expected, dict_util.replace_placeholders(dct, variables))

    def test_replace_variables_empty_var(self):
        dct = {
            "env": "{{env_var}}",
            "env_dict": {"env3": "{{ var1 }}"},
            "env4": "{{var2 }}",
            "env5": "{{{var2}}",
            "env6": "{{var3}}",
        }
        self.assertEqual(dct, dict_util.replace_placeholders(dct, {}))

    @mock.patch.dict(os.environ, {"LIMINAL_STAND_ALONE_MODE": "False"})
    @mock.patch('airflow.models.Variable.get')
    def test_replace_variables_flat_replace(self, airflow_variable_mock):
        def airflow_variable_values(key, default_var):
            return 'liminal playground' if key == 'playground' else default_var

        airflow_variable_mock.side_effect = airflow_variable_values

        dct = {
            "query": "select * from my_table " "where event_type = {{event_type}} and region = {{region}}",
            "env": "{{prod}}, {{stg}}, {{playground}}",
            "optional": "{{optionals}}",
        }

        variables = {
            "region": "us_east_1",
            "event_type": "subscription",
            "prod": "liminal production",
            "stg": "liminal staging",
        }

        expected = {
            'query': 'select * from my_table ' 'where event_type = subscription and region = us_east_1',
            "env": "liminal production, liminal staging, liminal playground",
            "optional": "{{optionals}}",
        }

        self.assertEqual(expected, dict_util.replace_placeholders(dct, variables))

    @mock.patch.dict(os.environ, {"LIMINAL_STAND_ALONE_MODE": "False"})
    @mock.patch('airflow.models.Variable.get')
    def test_replace_variables_with_nested_list(self, airflow_variable_mock):
        def airflow_variable_values(key, default_var):
            return 'liminal playground' if key == 'playground' else default_var

        airflow_variable_mock.side_effect = airflow_variable_values

        dct = {
            "query": "select * from my_table " "where event_type = {{event_type}} and region = {{region}}",
            "env": ['{{prod}}', '{{stg}}', '{{playground}}'],
            "tasks": [{'id': 'id1', 'image': '{{image}}'}],
            "optional": "{{optionals}}",
        }

        variables = {
            "region": "us_east_1",
            "event_type": "subscription",
            "prod": "liminal production",
            "stg": "liminal staging",
            "image": "my_image_name",
        }

        expected = {
            'env': ['liminal production', 'liminal staging', 'liminal playground'],
            'optional': '{{optionals}}',
            'query': 'select * from my_table where event_type = subscription and region = ' 'us_east_1',
            'tasks': [{'id': 'id1', 'image': 'my_image_name'}],
        }

        self.assertEqual(expected, dict_util.replace_placeholders(dct, variables))

    @mock.patch.dict(os.environ, {"table": "my_table", "LIMINAL_STAND_ALONE_MODE": "True"})
    def test_replace_variables_from_env(self):
        dct = {
            "query": "select * from my_table "
            "where event_type = {{event_type}} and region = {{region}} from {{table}}"
        }

        variables = {}

        expected = {
            'query': 'select * from my_table '
            'where event_type = {{event_type}} '
            'and region = {{region}} from my_table'
        }

        self.assertEqual(expected, dict_util.replace_placeholders(dct, variables))

    @mock.patch.dict(os.environ, {"table": "my_table", "LIMINAL_STAND_ALONE_MODE": "True"})
    def test_replace_variables_from_variable_and_not_env(self):
        dct = {
            "query": "select * from my_table "
            "where event_type = {{event_type}} and region = {{region}} from {{table}}"
        }

        variables = {"table": "my_variable_table"}

        expected = {
            'query': 'select * from my_table '
            'where event_type = {{event_type}} '
            'and region = {{region}} from my_variable_table'
        }

        self.assertEqual(expected, dict_util.replace_placeholders(dct, variables))

    @mock.patch.dict(os.environ, {"table": "my_table", "LIMINAL_STAND_ALONE_MODE": "False"})
    @mock.patch('airflow.models.Variable.get')
    def test_replace_variables_from_airflow_and_not_enc(self, airflow_variable_mock):
        def airflow_variable_values(key, default_var):
            return 'my_airflow_table' if key == 'table' else default_var

        airflow_variable_mock.side_effect = airflow_variable_values

        dct = {
            "query": "select * from my_table "
            "where event_type = {{event_type}} and region = {{region}} from {{table}}"
        }

        variables = {}

        expected = {
            'query': 'select * from my_table '
            'where event_type = {{event_type}} '
            'and region = {{region}} from my_airflow_table'
        }

        self.assertEqual(expected, dict_util.replace_placeholders(dct, variables))
