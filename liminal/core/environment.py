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
import subprocess

DEFAULT_DAGS_ZIP_NAME = 'liminal.zip'
DEFAULT_LIMINAL_HOME = os.path.expanduser('~/liminal_home')
DEFAULT_PIPELINES_SUBDIR = "pipelines"
LIMINAL_HOME_PARAM_NAME = "LIMINAL_HOME"
LIMINAL_HOME_CLOUD_PARAM_NAME = "AIRFLOW__CORE__LIMINAL_HOME"
LIMINAL_VERSION_PARAM_NAME = 'LIMINAL_VERSION'


def get_liminal_home():
    if LIMINAL_HOME_CLOUD_PARAM_NAME in os.environ:
        return os.environ.get(LIMINAL_HOME_CLOUD_PARAM_NAME)
    if not os.environ.get(LIMINAL_HOME_PARAM_NAME):
        logging.info("no environment parameter called LIMINAL_HOME detected")
        logging.info(f"registering {DEFAULT_LIMINAL_HOME} as the LIMINAL_HOME directory")
        os.environ[LIMINAL_HOME_PARAM_NAME] = DEFAULT_LIMINAL_HOME
    return os.environ.get(LIMINAL_HOME_PARAM_NAME, DEFAULT_LIMINAL_HOME)


def get_dags_dir():
    # if we are inside airflow, we will take it from the configured dags folder
    base_dir = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER", get_liminal_home())
    return os.path.join(base_dir, DEFAULT_PIPELINES_SUBDIR)


def get_liminal_version():
    result = os.environ.get(LIMINAL_VERSION_PARAM_NAME, None)
    if not result:
        output = subprocess.run(['pip freeze | grep \'apache-liminal\''], capture_output=True,
                                env=os.environ, shell=True)
        pip_res = output.stdout.decode('UTF-8').strip()
        liminal_home = get_liminal_home()
        whl_files = [file for file in os.listdir(liminal_home) if file.endswith(".whl")]
        if whl_files:
            value = 'file://' + os.path.join(liminal_home, whl_files[0])
        elif ' @ ' in pip_res:
            value = pip_res[pip_res.index(' @ ') + 3:]
        else:
            value = pip_res
        logging.info(f'LIMINAL_VERSION not set. Setting it to currently installed version: {value}')
        os.environ[LIMINAL_VERSION_PARAM_NAME] = value
    return os.environ.get(LIMINAL_VERSION_PARAM_NAME, 'apache-liminal')


def get_airflow_home_dir():
    # if we are inside airflow, we will take it from the configured dags folder
    base_dir = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER", get_liminal_home())
    return os.path.join(base_dir)
