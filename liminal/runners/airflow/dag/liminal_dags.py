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
from liminal.core import environment as env
from liminal.runners.airflow.dag import liminal_register_dags

from airflow import DAG

import traceback
import os

BASE_PATH=os.path.join(env.get_airflow_home_dir(), env.DEFAULT_PIPELINES_SUBDIR)

def register_dags(configs_path):
    dags = []
    pipelines = liminal_register_dags.register_dags(configs_path)

    for pipeline, dag in pipelines:
        try:
            globals()[pipeline] = dag
            dags.append(dag)
        except Exception:
            traceback.print_exc()

    return dags

register_dags(BASE_PATH)