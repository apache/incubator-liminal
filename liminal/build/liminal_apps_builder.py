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

from liminal.build.image_builder import ImageBuilder
from liminal.core.config.config import ConfigUtil
from liminal.core.util import class_util, files_util


def build_liminal_apps(path):
    """
    Build images for liminal apps in path.
    """
    config_util = ConfigUtil(path)
    configs = config_util.safe_load(is_render_variables=True)

    for liminal_config in configs:
        base_path = os.path.dirname(files_util.resolve_pipeline_source_file(liminal_config['name']))
        logging.info(base_path)

        for image in liminal_config.get('images', []):
            image_type = image['type']
            builder_class = __get_image_build_class(image_type)
            if builder_class:
                __build_image(base_path, image, builder_class)
            else:
                raise ValueError(f'No such image type: {image_type}')


def __build_image(base_path, builder_config, builder):
    if 'source' in builder_config:
        builder_instance = builder(
            config=builder_config,
            base_path=base_path,
            relative_source_path=builder_config['source'],
            tag=builder_config['image'])
        builder_instance.build()
    else:
        logging.info(f"No source provided for {builder_config['name']}, skipping.")


def __get_image_build_class(image_type):
    return image_build_types.get(image_type, None)


logging.info(f'Loading image builder implementations..')

# TODO: add configuration for user image builders package
image_builders_package = 'liminal.build.image'
# user_image_builders_package = 'TODO: user_image_builders_package'

task_build_types = class_util.find_subclasses_in_packages(
    [image_builders_package],
    ImageBuilder)


logging.info(f'Finished loading image builder implementations: {task_build_types}')
logging.info(f'Loading service image builder implementations..')

# TODO: add configuration for user service image builders package
service_builders_package = 'liminal.build.service'
# user_service_builders_package = 'TODO: user_service_builders_package'

service_build_types = class_util.find_subclasses_in_packages(
    [service_builders_package],
    ServiceImageBuilderMixin)

logging.info(f'Finished loading service image builder implementations: {service_build_types}')
