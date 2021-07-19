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

"""
This module contains CloudFormation create/delete stack operators.
Can be removed when Airflow 2.0.0 is released.
"""
from typing import List

from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.models import BaseOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from botocore.exceptions import ClientError


# noinspection PyAbstractClass
class CloudFormationHook(AwsBaseHook):
    """
    Interact with AWS CloudFormation.
    """

    def __init__(self, region_name=None, *args, **kwargs):
        self.region_name = region_name
        self.conn = None
        super().__init__(*args, **kwargs)

    def get_conn(self):
        self.conn = self.get_client_type('cloudformation', self.region_name)
        return self.conn


class BaseCloudFormationOperator(BaseOperator):
    """
    Base operator for CloudFormation operations.

    :param params: parameters to be passed to CloudFormation.
    :type dict
    :param aws_conn_id: aws connection to uses
    :type aws_conn_id: str
    """
    template_fields: List[str] = []
    template_ext = ()
    ui_color = '#1d472b'
    ui_fgcolor = '#FFF'

    @apply_defaults
    def __init__(
            self,
            params,
            aws_conn_id='aws_default',
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = params
        self.aws_conn_id = aws_conn_id

    def execute(self, context):
        self.log.info('Parameters: %s', self.params)

        self.cloudformation_op(CloudFormationHook(aws_conn_id=self.aws_conn_id).get_conn())

    def cloudformation_op(self, cloudformation):
        """
        This is the main method to run CloudFormation operation.
        """
        raise NotImplementedError()


class CloudFormationCreateStackOperator(BaseCloudFormationOperator):
    """
    An operator that creates a CloudFormation stack.

    :param params: parameters to be passed to CloudFormation. For possible arguments see:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
    :type dict
    :param aws_conn_id: aws connection to uses
    :type aws_conn_id: str
    """
    template_fields: List[str] = []
    template_ext = ()
    ui_color = '#6b9659'

    @apply_defaults
    def __init__(
            self,
            params,
            aws_conn_id='aws_default',
            *args, **kwargs):
        super().__init__(params=params, aws_conn_id=aws_conn_id, *args, **kwargs)

    def cloudformation_op(self, cloudformation):
        cloudformation.create_stack(**self.params)


class CloudFormationDeleteStackOperator(BaseCloudFormationOperator):
    """
    An operator that deletes a CloudFormation stack.

    :param params: parameters to be passed to CloudFormation. For possible arguments see:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack
    :type dict
    :param aws_conn_id: aws connection to uses
    :type aws_conn_id: str
    """
    template_fields: List[str] = []
    template_ext = ()
    ui_color = '#1d472b'
    ui_fgcolor = '#FFF'

    @apply_defaults
    def __init__(
            self,
            params,
            aws_conn_id='aws_default',
            *args, **kwargs):
        super().__init__(params=params, aws_conn_id=aws_conn_id, *args, **kwargs)

    def cloudformation_op(self, cloudformation):
        cloudformation.delete_stack(**self.params)


class BaseCloudFormationSensor(BaseSensorOperator):
    """
    Waits for a stack operation to complete on AWS CloudFormation.

    :param stack_name: The name of the stack to wait for (templated)
    :type stack_name: str
    :param aws_conn_id: ID of the Airflow connection where credentials and extra configuration are
        stored
    :type aws_conn_id: str
    :param poke_interval: Time in seconds that the job should wait between each try
    :type poke_interval: int
    """

    @apply_defaults
    def __init__(self,
                 stack_name,
                 complete_status,
                 in_progress_status,
                 aws_conn_id='aws_default',
                 poke_interval=30,
                 *args,
                 **kwargs):
        super().__init__(poke_interval=poke_interval, *args, **kwargs)
        self.aws_conn_id = aws_conn_id
        self.stack_name = stack_name
        self.complete_status = complete_status
        self.in_progress_status = in_progress_status
        self.hook = None

    def poke(self, context):
        """
        Checks for existence of the stack in AWS CloudFormation.
        """
        cloudformation = self.get_hook().get_conn()

        self.log.info('Poking for stack %s', self.stack_name)

        try:
            stacks = cloudformation.describe_stacks(StackName=self.stack_name)['Stacks']
            stack_status = stacks[0]['StackStatus']
            if stack_status == self.complete_status:
                return True
            elif stack_status == self.in_progress_status:
                return False
            else:
                raise ValueError(f'Stack {self.stack_name} in bad state: {stack_status}')
        except ClientError as e:
            if 'does not exist' in str(e):
                if not self.allow_non_existing_stack_status():
                    raise ValueError(f'Stack {self.stack_name} does not exist')
                else:
                    return True
            else:
                raise e

    def get_hook(self):
        """
        Gets the AwsGlueCatalogHook
        """
        if not self.hook:
            self.hook = CloudFormationHook(aws_conn_id=self.aws_conn_id)

        return self.hook

    def allow_non_existing_stack_status(self):
        """
        Boolean value whether or not sensor should allow non existing stack responses.
        """
        return False


class CloudFormationCreateStackSensor(BaseCloudFormationSensor):
    """
    Waits for a stack to be created successfully on AWS CloudFormation.

    :param stack_name: The name of the stack to wait for (templated)
    :type stack_name: str
    :param aws_conn_id: ID of the Airflow connection where credentials and extra configuration are
        stored
    :type aws_conn_id: str
    :param poke_interval: Time in seconds that the job should wait between each try
    :type poke_interval: int
    """

    template_fields = ['stack_name']
    ui_color = '#C5CAE9'

    @apply_defaults
    def __init__(self,
                 stack_name,
                 aws_conn_id='aws_default',
                 poke_interval=30,
                 *args,
                 **kwargs):
        super().__init__(stack_name=stack_name,
                         complete_status='CREATE_COMPLETE',
                         in_progress_status='CREATE_IN_PROGRESS',
                         aws_conn_id=aws_conn_id,
                         poke_interval=poke_interval,
                         *args,
                         **kwargs)


class CloudFormationDeleteStackSensor(BaseCloudFormationSensor):
    """
    Waits for a stack to be deleted successfully on AWS CloudFormation.

    :param stack_name: The name of the stack to wait for (templated)
    :type stack_name: str
    :param aws_conn_id: ID of the Airflow connection where credentials and extra configuration are
        stored
    :type aws_conn_id: str
    :param poke_interval: Time in seconds that the job should wait between each try
    :type poke_interval: int
    """

    template_fields = ['stack_name']
    ui_color = '#C5CAE9'

    @apply_defaults
    def __init__(self,
                 stack_name,
                 aws_conn_id='aws_default',
                 poke_interval=30,
                 *args,
                 **kwargs):
        super().__init__(stack_name=stack_name,
                         complete_status='DELETE_COMPLETE',
                         in_progress_status='DELETE_IN_PROGRESS',
                         aws_conn_id=aws_conn_id,
                         poke_interval=poke_interval, *args, **kwargs)

    def allow_non_existing_stack_status(self):
        return True
