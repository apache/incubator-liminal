from unittest import TestCase

from rainbow.build import build_rainbow


class Test(TestCase):
    def test_build_rainbow(self):
        build_rainbow.build_rainbow('tests/runners/airflow/rainbow')
