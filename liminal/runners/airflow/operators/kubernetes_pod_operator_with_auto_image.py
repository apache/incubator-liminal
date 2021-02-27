import logging
import re

from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.hooks.S3_hook import S3Hook

from liminal.runners.airflow.config import standalone_variable_backend

_S3_PROTOCOL = 's3://'
_S3_REGEX = '(.*){{(s3://.*)}}(.*)'


class KubernetesPodOperatorWithAutoImage(KubernetesPodOperator):
    """
    KubernetesPodOperator which finds deployed image from S3
    """

    def __init__(self,
                 *args,
                 **kwargs):
        namespace = kwargs.pop('namespace')
        image = kwargs.pop('image')
        name = kwargs.pop('name')
        self._LOG = logging.getLogger(self.__class__.__name__)

        super().__init__(
            namespace=namespace,
            image=image,
            name=name,
            *args,
            **kwargs)

    def execute(self, context):
        run_id = 'unknown_run_id'
        dag_run = context.get('dag_run')
        if dag_run:
            start_task_instance = dag_run.get_task_instance('start')
            run_id = start_task_instance.start_date.strftime('%Y%m%d%H%M%S')
            self._LOG.info(f'run_id = {run_id}')
        self.env_vars.update({'run_id': run_id})
        return super().execute(context)

    def render_template_fields(self, context, jinja_env=None):
        super().render_template_fields(context, jinja_env)
        s3_token = re.match(_S3_REGEX, self.image)
        if s3_token:
            image_commit_hash = self._get_image_commit_hash_from_s3(s3_token[2])
            image_prefix = s3_token[1]
            if image_commit_hash:
                self.image = image_prefix + image_commit_hash + s3_token[3]
            else:
                if image_prefix.endswith('-'):
                    self.image = image_prefix[:-1]
                else:
                    self.image = image_prefix
        self._LOG.info(f"image: {self.image}")

    def _get_image_commit_hash_from_s3(self, s3_path: str):
        self._LOG.info(f'Fetching version from {s3_path}')
        env = standalone_variable_backend.get_variable('env', 'default')
        if env != 'default':
            s3 = S3Hook().get_conn()
            s3_path = s3_path.replace(_S3_PROTOCOL, '')
            first_separator_index = s3_path.index('/')
            bucket = s3_path[:first_separator_index]
            prefix = s3_path[first_separator_index + 1:]
            objects = s3.list_objects(Bucket=bucket, Prefix=prefix)['Contents']
            last_added_key = [
                obj['Key'] for obj in
                sorted(objects, key=lambda obj: int(obj['LastModified'].strftime('%s')),
                       reverse=True)
            ][0]
            image = s3.get_object(Bucket=bucket, Key=last_added_key)['Body'].read().decode()
            image = image.split('-')[-1]
            return image
        else:
            return None
