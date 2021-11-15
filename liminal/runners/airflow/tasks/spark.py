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

from itertools import chain

from flatdict import FlatDict

from liminal.runners.airflow.tasks import hadoop, containerable


class SparkTask(hadoop.HadoopTask, containerable.ContainerTask):
    """
    Executes a Spark application.
    """

    def __init__(self, task_id, dag, parent, trigger_rule, liminal_config, pipeline_config,
                 task_config, variables=None):
        task_config['image'] = task_config.get('image', '')
        task_config['cmd'] = task_config.get('cmd', [])
        task_config['env_vars'] = {'SPARK_LOCAL_HOSTNAME': 'localhost'}
        super().__init__(task_id, dag, parent, trigger_rule, liminal_config,
                         pipeline_config, task_config, variables)

    def get_runnable_command(self):
        """
        Return spark-submit runnable command
        """
        return self.__generate_spark_submit()

    def __generate_spark_submit(self):
        spark_submit = ['spark-submit']

        spark_arguments = self.__spark_args()
        application_arguments = self.__additional_arguments()

        spark_submit.extend(spark_arguments)
        spark_submit.extend(application_arguments)

        return [str(x) for x in spark_submit]

    def __spark_args(self):
        # reformat spark conf
        flat_conf_args = list()

        spark_arguments = {
            'master': self.task_config.get('master', None),
            'class': self.task_config.get('class', None)
        }

        source_code = self.task_config.get("application_source")

        for conf_arg in ['{}={}'.format(k, v) for (k, v) in
                         FlatDict(self.task_config.get('conf', {})).items()]:
            flat_conf_args.append('--conf')
            flat_conf_args.append(conf_arg)

        spark_conf = self.__parse_spark_arguments(spark_arguments)
        spark_conf.extend(flat_conf_args)
        spark_conf.extend([source_code])
        return spark_conf

    def __additional_arguments(self):
        application_arguments = self.task_config.get('application_arguments', {})
        if type(application_arguments) == list:
            return application_arguments
        return self.__interleaving(application_arguments.keys(), application_arguments.values())

    def __parse_spark_arguments(self, spark_arguments):
        spark_arguments = {x[0]: x[1] for x in spark_arguments.items() if x[1]}

        return self.__interleaving([f'--{k}' for k in spark_arguments.keys() if spark_arguments[k]],
                                   spark_arguments.values())

    @staticmethod
    def __interleaving(keys, values):
        return list(chain.from_iterable(zip(keys, values)))

    def _kubernetes_cmds_and_arguments(self):
        return self.__generate_spark_submit(), []
