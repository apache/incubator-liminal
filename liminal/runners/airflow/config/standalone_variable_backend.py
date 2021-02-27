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

import logging
import os
from os import environ
from sqlite3 import OperationalError

from airflow.models import Variable

LIMINAL_STAND_ALONE_MODE_KEY = "LIMINAL_STAND_ALONE_MODE"


# noinspection PyBroadException
def get_variable(key, default_val):
    if liminal_local_mode():
        return os.environ.get(key, default_val)
    else:
        try:
            return Variable.get(key, default_var=default_val)
        except OperationalError as e:
            logging.warning(
                f'Failed to find variable {key} in Airflow variables table.'
                f' Error: {e.__class__.__module__}.{e.__class__.__name__}'
            )
        except Exception as e:
            logging.warning(f'Failed to find variable {key} in Airflow variables table. Error: {e}')
            return default_val


def liminal_local_mode():
    stand_alone = environ.get(LIMINAL_STAND_ALONE_MODE_KEY, "False")
    return stand_alone.strip().lower() == "true"
