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

import yaml
from flask import Flask, request, Blueprint


def __get_module(kls):
    parts = kls.split('.')
    module = ".".join(parts)
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def __get_endpoint_function(endpoint_config):
    module = __get_module(endpoint_config['module'])
    return module.__getattribute__(endpoint_config['function'])


if __name__ == '__main__':
    with open('service.yml') as stream:
        config = yaml.safe_load(stream)

    endpoints = {
        endpoint_config['endpoint'][1:]: __get_endpoint_function(endpoint_config)
        for endpoint_config in config['endpoints']
    }

    blueprint = Blueprint('liminal_python_server_blueprint', __name__)


    @blueprint.route('/favicon.ico', methods=('GET', 'POST'))
    def no_content():
        return '', 204


    @blueprint.route('/', defaults={'endpoint': ''}, methods=('GET', 'POST'))
    @blueprint.route('/<endpoint>', methods=('GET', 'POST'))
    def show(endpoint):
        if endpoint in endpoints:
            return endpoints[endpoint](request.get_data())
        else:
            return 'Page not found.', 404


    app = Flask(__name__)
    app.register_blueprint(blueprint)

    app.run(host='0.0.0.0', threaded=False, port=80)
