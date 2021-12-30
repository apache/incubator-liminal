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

from liminal.core.config.config import ConfigUtil
from liminal.core.util import class_util, files_util, extensible


def build_liminal_apps(path):
    """
    Build images for liminal apps in path.
    """
    config_util = ConfigUtil(path)
    configs = config_util.safe_load(is_render_variables=True, soft_merge=True)

    for liminal_config in configs:
        base_path = os.path.dirname(files_util.resolve_pipeline_source_file(liminal_config['name']))
        if 'images' in liminal_config:
            for image in liminal_config['images']:
                image_name = image['image']

                if 'source' in image:
                    image_type = image['type']
                    builder_class = __get_image_builder_class(image_type)
                    if builder_class:
                        __build_image(base_path, image, builder_class)
                    else:
                        raise ValueError(f'No such image type: {image_type}')
                else:
                    logging.warning(f'No source configured for image {image_name}.')


def __build_image(base_path, builder_config, builder):
    builder_instance = builder(
        config=builder_config,
        base_path=base_path,
        relative_source_path=builder_config['source'],
        tag=builder_config['image'],
    )
    builder_instance.build()


def __get_image_builder_class(task_type):
    return image_builder_types.get(task_type, None)


logging.info(f'Loading image builder implementations..')

image_builder_types = extensible.load_image_builders()
print(image_builder_types)

logging.info(f'Finished loading image builder implementations: {image_builder_types}')
logging.info(f'Loading service image builder implementations..')
