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
import traceback

import yaml
from ddtrace import patch_all
from flask import Flask, request
from pythonjsonlogger import jsonlogger

app = Flask(__name__)

# noinspection PyTypeChecker
patch_all(logging=True)

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

LOG = logging.getLogger("liminal_python_server")


def start_server(yml_path):
    with open(yml_path) as stream:
        __start_server(yaml.safe_load(stream))


# noinspection PyUnresolvedReferences
def __start_server(config):
    globals()['request'] = __import__('flask').request

    endpoints = config['endpoints']

    for endpoint_config in endpoints:
        LOG.info(f'Registering endpoint: {endpoint_config}')
        endpoint = endpoint_config['endpoint']

        module = __get_module(endpoint_config['module'])

        function = module.__getattribute__(endpoint_config['function'])

        app.add_url_rule(rule=endpoint,
                         endpoint=endpoint,
                         view_func=LambdaWrapper(function).get_lambda(),
                         methods=['GET', 'POST'])

    LOG.info('Starting python server')


class LambdaWrapper:

    def __init__(self, function):
        self.function = function

    def get_lambda(self):
        if os.environ.get('USE_LAMBDA_IN_SERVING', 'true').lower() == 'true':
            return lambda: self.function(
                request.data
            )
        else:
            return self.wrapper

    def wrapper(self):
        return self.function(
            request.get_data()
        )


def __get_module(kls):
    parts = kls.split('.')
    module = ".".join(parts)
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


@app.errorhandler(Exception)
def handle_error(error):
    LOG.info(traceback.format_exception_only(type(error), error))
    return "Internal server error, contact service owner.", 500


start_server('service.yml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=False, port=80)
