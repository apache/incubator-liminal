import os
import tempfile
import unittest
from unittest import TestCase

from liminal.build.image.python.python import PythonImageBuilder
from liminal.kubernetes import volume_util
from liminal.runners.airflow import DummyDag
from liminal.runners.airflow.executors.kubernetes import KubernetesPodExecutor
from liminal.runners.airflow.tasks import python
from tests.util import dag_test_utils


class TestPythonTask(TestCase):
    if os.getenv('POD_NAMESPACE') == "jenkins":
        _VOLUME_NAME = 'unittest'
    else:
        _VOLUME_NAME = 'myvol1'

    _WRITE_INPUTS_IMG = 'write_inputs_img'
    _WRITE_OUTPUTS_IMG = 'write_outputs_img'

    @classmethod
    def setUpClass(cls) -> None:
        base_path = os.path.join(os.path.dirname(__file__), '../../apps/app_with_volumes')

        config = {}

        PythonImageBuilder(config=config,
                           base_path=base_path,
                           relative_source_path='write_inputs',
                           tag=cls._WRITE_INPUTS_IMG).build()

        PythonImageBuilder(config=config,
                           base_path=base_path,
                           relative_source_path='write_outputs',
                           tag=cls._WRITE_OUTPUTS_IMG).build()

    def setUp(self) -> None:
        if not os.getenv('POD_NAMESPACE') == "jenkins":
            volume_util.delete_local_volume(self._VOLUME_NAME)

        os.environ['TMPDIR'] = '/tmp'

        if os.getenv('POD_NAMESPACE') == "jenkins":
            self.temp_dir = '/mnt/vol1'
            self.sub_path_dir = "unittests"
            self.temp_dir = os.path.join(self.temp_dir, self.sub_path_dir)
        else:
            self.temp_dir = tempfile.mkdtemp()
            self.sub_path_dir = ""

        self.liminal_config = {
            'volumes': [
                {
                    'volume': self._VOLUME_NAME,
                    'local': {
                        'path': self.temp_dir.replace(
                            "/var/folders",
                            "/private/var/folders"
                        )
                    }
                }
            ]
        }

        if not os.getenv('POD_NAMESPACE') == "jenkins":
            volume_util.create_local_volumes(self.liminal_config, None)

    def test_apply_task_to_dag(self):
        dag = dag_test_utils.create_dag()

        task0 = self.__create_python_task(dag,
                                          'my_input_task',
                                          [],
                                          self._WRITE_INPUTS_IMG,
                                          'python -u write_inputs.py',
                                          env_vars={
                                              'NUM_FILES': 10,
                                              'NUM_SPLITS': '{{NUM_SPLITS}}'
                                          })
        task0.apply_task_to_dag()

        task1 = self.__create_python_task(dag,
                                          'my_output_task',
                                          [dag.tasks[0]],
                                          '{{image}}',
                                          'python -u write_outputs.py',
                                          env_vars={
                                              'NUM_SPLITS': '{{NUM_SPLITS}}'
                                          })
        task1.apply_task_to_dag()

        for task in dag.tasks:
            print(f'Executing task {task.task_id}')
            dummy_dag = DummyDag('my_dag', task.task_id).context
            dummy_dag.get('dag_run').conf = {'image': self._WRITE_OUTPUTS_IMG,
                                             'NUM_SPLITS': 3}
            task.execute(dummy_dag)

        inputs_dir = os.path.join(self.temp_dir, 'inputs')
        outputs_dir = os.path.join(self.temp_dir, 'outputs')

        self.assertListEqual(os.listdir(self.temp_dir), ['outputs', 'inputs'])

        inputs_dir_contents = sorted(os.listdir(inputs_dir))

        self.assertListEqual(inputs_dir_contents, ['0', '1', '2'])

        self.assertListEqual(sorted(os.listdir(os.path.join(inputs_dir, '0'))),
                             ['input0.json', 'input3.json', 'input6.json', 'input9.json'])

        self.assertListEqual(sorted(os.listdir(os.path.join(inputs_dir, '1'))),
                             ['input1.json', 'input4.json', 'input7.json'])

        self.assertListEqual(sorted(os.listdir(os.path.join(inputs_dir, '2'))),
                             ['input2.json', 'input5.json', 'input8.json'])

        self.assertListEqual(sorted(os.listdir(outputs_dir)),
                             ['output0.txt', 'output1.txt',
                              'output2.txt', 'output3.txt',
                              'output4.txt', 'output5.txt',
                              'output6.txt', 'output7.txt',
                              'output8.txt', 'output9.txt'])

        for filename in os.listdir(outputs_dir):
            with open(os.path.join(outputs_dir, filename)) as f:
                expected_file_content = filename.replace('output', 'myval').replace('.txt', '')
                self.assertEqual(f.read(), expected_file_content)

    def __create_python_task(self,
                             dag,
                             task_id,
                             parent,
                             image,
                             cmd,
                             env_vars=None):

        self.liminal_config['executors'] = [
            {
                'executor': 'k8s',
                'type': 'kubernetes',
            }
        ]

        task_config = {
            'task': task_id,
            'cmd': cmd,
            'image': image,
            'executor': 'k8s',
            'env_vars': env_vars if env_vars is not None else {},
            'mounts': [
                {
                    'mount': 'mymount',
                    'volume': self._VOLUME_NAME,
                    'path': '/mnt/vol1',
                    'sub_path': self.sub_path_dir
                }
            ]
        }

        return python.PythonTask(task_id=task_id,
                                 dag=dag,
                                 parent=parent,
                                 trigger_rule='all_success',
                                 liminal_config=self.liminal_config,
                                 pipeline_config={
                                     'pipeline': 'my_pipeline'
                                 },
                                 task_config=task_config,
                                 executor=KubernetesPodExecutor(
                                     task_id='k8s',
                                     liminal_config=self.liminal_config,
                                     executor_config={
                                         'executor': 'k8s'
                                     }
                                 ))


if __name__ == '__main__':
    unittest.main()
