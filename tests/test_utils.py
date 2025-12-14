import unittest

import numpy as np
import pandas as pd

from medpriv.utils.misc import calculate_median, concatenate_dataframes


class TestMisc(unittest.TestCase):
    def test_calculate_median(self):
        values = [1, 2, 3, 4, 5, 6, 7, 8]
        expected_median = 4.5
        self.assertEqual(calculate_median(values), expected_median)
