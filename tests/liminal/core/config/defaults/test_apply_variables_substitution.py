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

from unittest import TestCase

from liminal.core.config.defaults import default_configs


class TestApplyVariablesSubstitution(TestCase):
    def test_apply(self):
        subliminal = {'variables': {
            'one': 'one_value',
            'two': 'two_value'
        }}

        superliminal = {'variables': {
            'three': 'three_value',
            'two': 'two_super_value'
        }}

        expected = {'variables': {
            'one': 'one_value',
            'two': 'two_value',
            'three': 'three_value'
        }}
        self.assertEqual(expected, default_configs.apply_variable_substitution(subliminal, superliminal))

    def test_apply_superliminal_is_missing_variables(self):
        subliminal = {'variables': {
            'one': 'one_value',
            'two': 'two_value'
        }}

        superliminal = {}

        expected = {'variables': {
            'one': 'one_value',
            'two': 'two_value'
        }}
        self.assertEqual(expected, default_configs.apply_variable_substitution(subliminal, superliminal))

    def test_apply_subliminal_is_missing_variables(self):
        subliminal = {}

        superliminal = {'variables': {
            'one': 'one_value',
            'two': 'two_value'
        }}

        expected = {'variables': {
            'one': 'one_value',
            'two': 'two_value'
        }}
        self.assertEqual(expected, default_configs.apply_variable_substitution(subliminal, superliminal))
