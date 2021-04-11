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

from liminal.core import environment
from liminal.core.config.defaults import base, default_configs
from liminal.core.util import dict_util
from liminal.core.util import files_util


class ConfigUtil:
    """
    Load and enrich config files under configs_path.
    """
    __BASE = "base"
    __PIPELINES = "pipelines"
    __SUPER = "super"
    __TYPE = "type"
    __SUB = "sub"
    __SERVICES = "services"
    __TASKS = "tasks"
    __PIPELINE_DEFAULTS = "pipeline_defaults"
    __BEFORE_TASKS = "before_tasks"
    __AFTER_TASKS = "after_tasks"

    def __init__(self, configs_path):
        self.configs_path = configs_path
        self.config_files = files_util.load(configs_path)
        self.base = base.BASE
        self.loaded_subliminals = []
        self.snapshot_path = os.path.join(environment.get_airflow_home_dir(),
                                          '../liminal_config_files')

    def safe_load(self, is_render_variables):
        """
        :returns list of config files after enrich with defaults and supers
        """
        if self.loaded_subliminals:
            return self.loaded_subliminals

        configs = self.config_files.values()
        enriched_configs = []

        for subliminal in [config for config in configs if self.__is_subliminal(config)]:
            name = subliminal.get('name')
            logging.info(f'Loading yml {name}')
            # noinspection PyBroadException
            try:
                superliminal = self.__get_superliminal(subliminal)
                enriched_config = self.__merge_configs(subliminal, superliminal,
                                                       is_render_variables)
                enriched_configs.append(enriched_config)
            except Exception:
                logging.error(f'Failed to load yml {name}')
                traceback.print_exc()

        self.loaded_subliminals = enriched_configs

        return self.loaded_subliminals

    def __merge_configs(self, subliminal, superliminal, is_render_variables):
        if not superliminal:
            return subliminal

        sub = subliminal.copy()
        supr = superliminal.copy()

        merged_superliminal = self.__merge_configs(supr, self.__get_superliminal(supr),
                                                   is_render_variables)

        if self.__is_subliminal(sub):
            return self.__merge_sub_and_super(sub, merged_superliminal, is_render_variables)
        else:
            return self.__merge_superliminals(sub, merged_superliminal)

    def __get_superliminal(self, liminal):
        superliminal = {}
        if not self.__is_base_config(liminal):
            superliminal_name = liminal.get(self.__SUPER, '')
            if not superliminal_name:
                superliminal = self.base
            else:
                superliminal = self.__get_config(superliminal_name)

                if not superliminal:
                    raise FileNotFoundError(
                        f"superliminal '{superliminal_name}' is missing from '{self.configs_path}'")

        return superliminal

    def __get_base_config(self):
        return self.base

    def __is_base_config(self, config):
        return config.get('name', '') == self.__BASE

    def __is_subliminal(self, config):
        is_subliminal = config.get(self.__TYPE, self.__SUB) != self.__SUPER
        if is_subliminal:
            config[self.__TYPE] = self.__SUB
        return is_subliminal

    def __get_config(self, config_name):
        return self.config_files.get(config_name)

    def __merge_sub_and_super(self, sub, supr, is_render_variables):
        merged_pipelines = list()

        for pipeline in sub.get(self.__PIPELINES, {}):
            final_pipeline = self.__apply_pipeline_defaults(sub, supr, pipeline)
            merged_pipelines.append(final_pipeline)

        sub[self.__PIPELINES] = merged_pipelines
        sub[self.__SERVICES] = default_configs.apply_service_defaults(sub, supr)

        sub = dict_util.merge_dicts(supr.copy(), sub)

        return default_configs.apply_variable_substitution(sub, supr, is_render_variables)

    def __merge_superliminals(self, super1, super2):
        super1_pipeline_defaults = super1.get(self.__PIPELINE_DEFAULTS, {}).copy()
        super2_pipeline_defaults = super2.get(self.__PIPELINE_DEFAULTS, {}).copy()

        super1[self.__PIPELINE_DEFAULTS][self.__BEFORE_TASKS] = \
            super2_pipeline_defaults.pop(self.__BEFORE_TASKS, []) + super1_pipeline_defaults.pop(
                self.__BEFORE_TASKS, [])

        super1[self.__PIPELINE_DEFAULTS][self.__AFTER_TASKS] = \
            super1_pipeline_defaults.pop(self.__AFTER_TASKS, []) + super2_pipeline_defaults.pop(
                self.__AFTER_TASKS, [])

        # merge supers tasks
        return dict_util.merge_dicts(super1, super2, True)

    def snapshot_final_liminal_configs(self):
        files_util.dump_liminal_configs(liminal_configs=self.loaded_subliminals,
                                        path=self.snapshot_path)

    @staticmethod
    def __apply_pipeline_defaults(subliminal, superliminal, pipeline):
        return default_configs.apply_pipeline_defaults(subliminal, superliminal, pipeline)
