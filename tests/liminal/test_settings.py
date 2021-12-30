from unittest import TestCase, mock

from liminal import settings
from liminal.core.util import class_util
from liminal.runners.airflow.model import executor as liminal_executor


class TestSettings(TestCase):
    @mock.patch("os.makedirs", mock.Mock(return_value=0))
    def test_set(self):
        settings.initialize()
        executors_by_liminal_name = class_util.find_subclasses_in_packages(
            ['plugins.executors'],
            liminal_executor.Executor)
        print(executors_by_liminal_name)
