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
from airflow.operators.bash import BashOperator

from liminal.runners.airflow.model import task


class CustomTask(task.Task):
    def custom_task_logic(self):
        hello_world = BashOperator(
            task_id='hello_world',
            bash_command='echo "hello from liminal custom task"',
        )

        if self.parent:
            self.parent.set_downstream(hello_world)

        return hello_world
