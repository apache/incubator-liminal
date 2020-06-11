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
from os import environ

from airflow.models import Variable

RAINBOW_STAND_ALONE_MODE_KEY = "RAINBOW_STAND_ALONE_MODE"


def get_variable(key, default_val):
    if rainbow_local_mode():
        return os.environ.get(key, default_val)
    else:
        return Variable.get(key, default_var=default_val)


def rainbow_local_mode():
    stand_alone = environ.get(RAINBOW_STAND_ALONE_MODE_KEY, "False")
    return stand_alone.strip().lower() == "true"
