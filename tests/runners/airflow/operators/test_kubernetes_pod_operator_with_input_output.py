import unittest
from unittest import TestCase
import itertools

from liminal.runners.airflow.operators.\
    kubernetes_pod_operator_with_input_output import _split_list


class TestSplitList(TestCase):
    def setUp(self) -> None:
        self.short_seq = [{f'task_{i}': f'value_{i}'} for i in range(3)]
        self.long_seq = [{f'task_{i}': f'value_{i}'} for i in range(10)]

    def test_seq_equal_num(self):
        num = len(self.short_seq)
        result = _split_list(self.short_seq, num)
        expected = [[{'task_0': 'value_0'}], [{'task_1': 'value_1'}],
                    [{'task_2': 'value_2'}]]
        self.assertListEqual(expected, result)

    def test_seq_grater_than_num(self):
        num = 3
        result = _split_list(self.long_seq, num)
        n_tasks = len(self.long_seq)

        min_length = min([len(i) for i in result])
        max_length = max([len(i) for i in result])
        flat_results = list(itertools.chain(*result))

        self.assertGreaterEqual(max_length - min_length, 1)
        self.assertEqual(n_tasks, len(flat_results))
        self.assertTrue(all([{f'task_{i}': f'value_{i}'} in flat_results
                             for i in range(n_tasks)]))

    def test_seq_smaller_than_num(self):
        test_num_range = [8, 9, 10, 11, 12]
        for num in test_num_range:
            result = _split_list(self.short_seq, num)
            self.assertEqual(len(result), num)
            self.assertTrue(all([[i] in result for i in self.short_seq]))
            self.assertEqual([[]] * (num - len(self.short_seq)),
                             [i for i in result if i == []])

