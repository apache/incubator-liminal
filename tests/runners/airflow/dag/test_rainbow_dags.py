from unittest import TestCase

from rainbow.runners.airflow.dag import rainbow_dags
import unittest


class Test(TestCase):
    def test_register_dags(self):
        dags = rainbow_dags.register_dags('tests/runners/airflow/rainbow')
        self.assertEqual(len(dags), 1)
        # TODO: elaborate test
        pass


if __name__ == '__main__':
    unittest.main()
