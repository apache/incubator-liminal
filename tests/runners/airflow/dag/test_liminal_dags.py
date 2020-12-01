import os
import unittest
from unittest import TestCase

from liminal.runners.airflow.dag import liminal_dags
from liminal.runners.airflow.operators.job_status_operator import JobEndOperator, JobStartOperator

class Test(TestCase):
    def test_register_dags(self):
        dags = self.get_register_dags()

        self.assertEqual(len(dags), 1)

        test_pipeline = dags[0]

        # TODO: elaborate tests to assert all dags have correct tasks
        self.assertEqual(test_pipeline.dag_id, 'my_pipeline')

    def test_default_start_task(self):
        dags = self.get_register_dags()

        task_dict = dags[0].task_dict

        self.assertIsInstance(task_dict['start'], JobStartOperator)

    def test_default_end_task(self):
        dags = self.get_register_dags()

        task_dict = dags[0].task_dict

        self.assertIsInstance(task_dict['end'], JobEndOperator)

    def test_default_args(self):
        dag = self.get_register_dags()[0]
        default_args = dag.default_args

        keys = default_args.keys()
        self.assertIn('default_arg_loaded', keys)
        self.assertIn('default_array_loaded', keys)
        self.assertIn('default_object_loaded', keys)

    @staticmethod
    def get_register_dags():
        base_path = os.path.join(os.path.dirname(__file__), '../liminal')
        return liminal_dags.register_dags(base_path)


if __name__ == '__main__':
    unittest.main()
