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
import pathlib
from unittest import TestCase

from termcolor import colored

EXCLUDED_EXTENSIONS = ['.gif', '.png', '.pyc', 'LICENSE', 'DISCLAIMER', 'DISCLAIMER-WIP', 'NOTICE', '.whl']
EXCLUDED_DIRS = ['docs/build', 'build', 'dist', '.git', '.idea', 'venv', 'apache_liminal.egg-info']
EXCLUDED_FILES = ['DISCLAIMER-WIP']

PYTHON_LICENSE_HEADER = """
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
""".strip().split(
    "\n"
)

MD_LICENSE_HEADER = """
<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->
""".strip().split(
    "\n"
)

RST_LICENSE_HEADER = """
..
   Licensed to the Apache Software Foundation (ASF) under one
   or more contributor license agreements.  See the NOTICE file
   distributed with this work for additional information
   regarding copyright ownership.  The ASF licenses this file
   to you under the Apache License, Version 2.0 (the
   "License"); you may not use this file except in compliance
   with the License.  You may obtain a copy of the License at
..

..  http://www.apache.org/licenses/LICENSE-2.0

..
   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
..
""".strip().split(
    "\n"
)

BAT_LICENSE_HEADER = """
REM
REM Licensed to the Apache Software Foundation (ASF) under one
REM or more contributor license agreements.  See the NOTICE file
REM distributed with this work for additional information
REM regarding copyright ownership.  The ASF licenses this file
REM to you under the Apache License, Version 2.0 (the
REM "License"); you may not use this file except in compliance
REM with the License.  You may obtain a copy of the License at
REM
REM   http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing,
REM software distributed under the License is distributed on an
REM "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
REM KIND, either express or implied.  See the License for the
REM specific language governing permissions and limitations
REM under the License.
""".strip().split(
    "\n"
)

JSON_LICENSE_HEADER = """
  "": [
    "Licensed to the Apache Software Foundation (ASF) under one",
    "or more contributor license agreements.  See the NOTICE file",
    "distributed with this work for additional information",
    "regarding copyright ownership.  The ASF licenses this file",
    "to you under the Apache License, Version 2.0 (the",
    "\\"License\\"); you may not use this file except in compliance",
    "with the License.  You may obtain a copy of the License at",
    "",
    "  http://www.apache.org/licenses/LICENSE-2.0",
    "",
    "Unless required by applicable law or agreed to in writing,",
    "software distributed under the License is distributed on an",
    "\\"AS IS\\"BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY",
    "KIND, either express or implied.  See the License for the",
    "specific language governing permissions and limitations",
    "under the License."
  ],
""".strip().split(
    "\n"
)


class TestLicenses(TestCase):
    def test_licenses(self):
        files = []
        base_dir = os.path.join(pathlib.Path(__file__).parent.parent.absolute())
        print(f'Checking licenses for files in {base_dir}')
        for r, d, f in os.walk(base_dir):
            if not any(os.path.relpath(r, base_dir).startswith(excluded) for excluded in EXCLUDED_DIRS):
                for file in f:
                    if (
                        not any(os.path.basename(file).endswith(ext) for ext in EXCLUDED_EXTENSIONS)
                        and not os.path.basename(file) in EXCLUDED_FILES
                    ):
                        files.append(os.path.join(r, file))

        output = ''
        files_missing_license = []
        success = True
        for file in files:
            print(f'Checking license for file {file}')
            has_license = self.check_license(file)
            if not has_license:
                output += colored(f'Missing License: {file}\n', 'red')
                files_missing_license.append(file)
            success = success and has_license

        print(output)

        if not success:
            self.assertListEqual([], files_missing_license)

    @staticmethod
    def check_license(file):
        header_lines = PYTHON_LICENSE_HEADER
        if file.endswith('.md'):
            header_lines = MD_LICENSE_HEADER
        elif file.endswith('.rst'):
            header_lines = RST_LICENSE_HEADER
        elif file.endswith('.bat'):
            header_lines = BAT_LICENSE_HEADER
        elif file.endswith('.json'):
            header_lines = JSON_LICENSE_HEADER
            header_lines[0] = f'  {header_lines[0]}'
        with open(file) as f:
            file_lines = f.readlines()
        return all(f'{line}\n' in file_lines for line in header_lines)
