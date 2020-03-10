from unittest import TestCase

from rainbow.runners.airflow.dag import rainbow_dags


class Test(TestCase):
    def test_register_dags(self):
        dags = rainbow_dags.register_dags("tests/runners/airflow/dag/rainbow")
        self.assertEqual(len(dags), 1)
        # TODO: elaborate test
        pass
