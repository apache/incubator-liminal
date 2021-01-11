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
from logging.handlers import RotatingFileHandler

from liminal.core import environment

LOGS_DIR = 'logs'
LOG_FILENAME = 'liminal.log'
MAX_FILE_SIZE = 10485760  # 10 MB


def logging_initialization():
    root_logger = logging.getLogger()

    log_formatter = logging.Formatter(
        '[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s',
        '%m-%d %H:%M:%S'
    )

    logs_dir = os.path.join(environment.get_liminal_home(), LOGS_DIR)
    os.makedirs(logs_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, LOG_FILENAME),
        maxBytes=MAX_FILE_SIZE,
        backupCount=3
    )

    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    [h.setFormatter(log_formatter) for h in root_logger.handlers]

    logging.info('Logging initialization completed')
