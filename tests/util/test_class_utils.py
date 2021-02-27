from unittest import TestCase

from liminal.core.util import class_util
from tests.util.test_pkg_1.test_clazz_base import A
from tests.util.test_pkg_1.test_pkg_1_1.test_clazz_child_1 import B
from tests.util.test_pkg_1.test_pkg_1_1.test_clazz_child_2 import C
from tests.util.test_pkg_1.test_pkg_1_1.test_pkg_1_1_1.test_clazz_leaf_1 import D
from tests.util.test_pkg_1.test_pkg_1_1.test_pkg_1_1_2.test_clazz_leaf_2 import E


class Test(TestCase):
    def test_find_full_hierarchy_from_root(self):
        expected_set = {
            'test_clazz_child_1': B,
            'test_clazz_child_2': C,
            'test_clazz_leaf_1': D,
            'test_clazz_leaf_2': E
        }
        self.hierarchy_check(A, expected_set)

    def hierarchy_check(self, clazz, expected_dict):
        pkg_root = 'tests.util.test_pkg_1'
        result_dict = class_util.find_subclasses_in_packages([pkg_root], clazz)
        self.assertDictEqual(result_dict, expected_dict)
