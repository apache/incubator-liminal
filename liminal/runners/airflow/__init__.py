##
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

from datetime import datetime
from unittest.mock import MagicMock

import pytz


class DummyDagRun:

    def __init__(self) -> None:
        self.start_date = pytz.utc.localize(datetime.utcnow())
        self.conf = None
        self.run_id = "run_id"

    @staticmethod
    def get_task_instances():
        return []

    def get_task_instance(self, _):
        return self


class DummyDag:

    def __init__(self, dag_id, task_id):
        self.dag_id = dag_id
        self.task_id = task_id
        self.try_number = 0
        self.is_subdag = False
        self.execution_date = '2017-05-21T00:00:00'
        self.dag_run_id = 'dag_run_id'
        self.owner = ['owner1', 'owner2']
        self.email = ['email1@test.com']
        self.task = MagicMock(name='task', owner=self.owner, email=self.email)
        self.context = {
            'dag': self,
            'task': self,
            'ti': self,
            'ts': datetime.now().timestamp(),
            'dag_run': DummyDagRun()
        }

    def get_dagrun(self):
        return self.context['dag_run']

    @staticmethod
    def xcom_push(key, value):
        return key, value
