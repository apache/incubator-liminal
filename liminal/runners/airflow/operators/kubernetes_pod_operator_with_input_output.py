import json

from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator


def split_list(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


_IS_SPLIT_KEY = 'is_split'


class PrepareInputOperator(KubernetesPodOperator):

    def __init__(self,
                 input_type=None,
                 input_path=None,
                 split_input=False,
                 executors=1,
                 *args,
                 **kwargs):
        namespace = kwargs['namespace']
        image = kwargs['image']
        name = kwargs['name']

        del kwargs['namespace']
        del kwargs['image']
        del kwargs['name']

        super().__init__(
            namespace=namespace,
            image=image,
            name=name,
            *args,
            **kwargs)

        self.input_type = input_type
        self.input_path = input_path
        self.executors = executors
        self.split_input = split_input

    def execute(self, context):
        input_dict = {}

        self.log.info(f'config type: {self.input_type}')

        ti = context['task_instance']

        if self.input_type:
            if self.input_type == 'file':
                input_dict = {}  # future feature: return config from file
            elif self.input_type == 'sql':
                input_dict = {}  # future feature: return from sql config
            elif self.input_type == 'task':
                self.log.info(self.input_path)
                input_dict = ti.xcom_pull(task_ids=self.input_path)
            elif self.input_type == 'static':
                input_dict = json.loads(self.input_path)
            else:
                raise ValueError(f'Unknown config type: {self.input_type}')

        run_id = context['dag_run'].run_id
        print(f'run_id = {run_id}')

        if input_dict:
            self.log.info(f'Generated input: {input_dict}')

            if self.split_input:
                input_splits = split_list(input_dict, self.executors)

                ti.xcom_push(key=_IS_SPLIT_KEY, value=True)

                return input_splits
            else:
                return input_dict
        else:
            return {}

    def run_pod(self, context):
        return super().execute(context)


class KubernetesPodOperatorWithInputAndOutput(KubernetesPodOperator):
    """
    TODO: pydoc
    """

    _LIMINAL_INPUT_ENV_VAR = 'LIMINAL_INPUT'

    def __init__(self,
                 task_split,
                 input_task_id=None,
                 *args,
                 **kwargs):
        namespace = kwargs['namespace']
        image = kwargs['image']
        name = kwargs['name']

        del kwargs['namespace']
        del kwargs['image']
        del kwargs['name']

        super().__init__(
            namespace=namespace,
            image=image,
            name=name,
            *args,
            **kwargs)

        self.input_task_id = input_task_id
        self.task_split = task_split

    def execute(self, context):
        task_input = {}

        if self.input_task_id:
            ti = context['task_instance']

            self.log.info(f'Fetching input for task {self.task_split}.')

            task_input = ti.xcom_pull(task_ids=self.input_task_id)

            is_split = ti.xcom_pull(task_ids=self.input_task_id, key=_IS_SPLIT_KEY)
            self.log.info(f'is_split = {is_split}')
            if is_split:
                self.log.info(f'Fetching split {self.task_split} of input.')

                task_input = task_input[self.task_split]

        if task_input:
            self.log.info(f'task input = {task_input}')

            self.env_vars.update({self._LIMINAL_INPUT_ENV_VAR: json.dumps(task_input)})
        else:
            self.env_vars.update({self._LIMINAL_INPUT_ENV_VAR: '{}'})

            self.log.info(f'Empty input for task {self.task_split}.')

        run_id = context['dag_run'].run_id
        print(f'run_id = {run_id}')

        self.env_vars.update({'run_id': run_id})
        return super().execute(context)
