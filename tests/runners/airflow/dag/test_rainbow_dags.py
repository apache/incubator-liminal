import os
import unittest
from unittest import TestCase

from rainbow.runners.airflow.dag import rainbow_dags
from rainbow.runners.airflow.operators.job_status_operator import JobEndOperator, JobStartOperator


class Test(TestCase):
    def test_register_dags(self):
        dags = self.get_register_dags()

        self.assertEqual(len(dags), 1)

        test_pipeline = dags[0]
        self.assertEqual(test_pipeline.dag_id, 'my_pipeline')

    def test_default_start_task(self):
        dags = self.get_register_dags()

        task_dict = dags[0].task_dict

        self.assertIsInstance(task_dict['start'], JobStartOperator)

    def test_default_end_task(self):
        dags = self.get_register_dags()

        task_dict = dags[0].task_dict

        self.assertIsInstance(task_dict['end'], JobEndOperator)

    @staticmethod
    def get_register_dags():
        base_path = os.path.join(os.path.dirname(__file__), '../rainbow')
        return rainbow_dags.register_dags(base_path)


if __name__ == '__main__':
    unittest.main()
