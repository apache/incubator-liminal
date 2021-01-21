#!/bin/sh

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

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if ! command -v liminal &> /dev/null
then
  liminal stop
fi

yes | pip uninstall apache-liminal

cd "$DIR" || exit

rm -rf build
rm -rf dist

python setup.py sdist bdist_wheel

rm scripts/*.whl

cp dist/*.whl scripts

ver=$(ls scripts/*.whl)
export LIMINAL_VERSION="apache-liminal @ file://$ver"

pip install scripts/*.whl

cd - || exit
