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
from liminal.core import environment
LIMINAL = 'liminal'
LOGS_DIR = 'logs'


def logging_initialization():
    # TBD - rotating file handler
    # TBD - log in JSON format
    root_logger = logging.getLogger()

    log_formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                                      '%m-%d %H:%M:%S')

    file_handler = logging.FileHandler("{0}/{1}/{2}.log".format(environment.get_liminal_home(), LOGS_DIR, LIMINAL))
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    # set the same format for all handlers
    [h.setFormatter(log_formatter) for h in root_logger.handlers]

    logging.info('Logging initialization completed')
