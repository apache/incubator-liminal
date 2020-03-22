import os
from unittest import TestCase

from rainbow.runners.airflow.dag import rainbow_dags
import unittest


class Test(TestCase):
    def test_register_dags(self):
        base_path = os.path.join(os.path.dirname(__file__), '../rainbow')
        dags = rainbow_dags.register_dags(base_path)
        self.assertEqual(len(dags), 1)
        # TODO: elaborate test
        pass


if __name__ == '__main__':
    unittest.main()
