import unittest

import pandas as pd

from medpriv.anonymize import EpsilonAnonymizer, KAnonymityAnonymizer
from medpriv.data_processing import EpsilonData, KAnonymityData


def getData():
    return {
        "name": ["Christian", "D", "C", "E", "F"],
        "age": ["23", "35", "45", "23", "35"],
        "zipcode": ["12345", "23456", "34567", "12345", "23456"],
        "gender": ["male", "female", "female", "female", "male"],
        "city": ["Berlin", "berlin", "Frankfurt", "frankFurt", "Stuttgart"],
        "income": ["high", "medium", "low", "medium", "low"],
    }


def getInputData():
    return pd.DataFrame(getData())


def getIdentifiers():
    return ["name"]


def getQuasiIdentifiersK():
    return [
        "age",
        "zipcode",
        "city",
        {"quid": "gender", "redactions": {"male": "gendered", "female": "gendered"}},
    ]


def getQuasiIdentfiersEpsilon():
    return ["age", "zipcode", "city", "gender"]


test = KAnonymityData(getInputData(), getQuasiIdentifiersK(), getIdentifiers())
test_data = KAnonymityAnonymizer(2, test)

# test_data.anonymize_partition()
test_data.generalize_partitions()
print(test_data.compute_initial_k_anonymity())


class TestKAnonymizer(unittest.TestCase):
    def setUp(self):
        self.data = KAnonymityData(getInputData(), getQuasiIdentifiersK(), getIdentifiers())
        self.anonymizeData = KAnonymityAnonymizer(2, self.data)

    def test_initial_k_anonymity(self):
        self.assertEqual(self.anonymizeData.compute_initial_k_anonymity(), 1)

    def test_anonymized_k_anonymity(self):
        self.anonymizeData.generalize_partitions()
        self.assertEqual(self.anonymizeData.compute_initial_k_anonymity(), 1)

    def test_anonymize_partition(self):
        expected = pd.DataFrame(
            {
                "name": {0: "*", 1: "*", 2: "*", 3: "*", 4: "*"},
                "age": {0: "23", 1: "35", 2: "45", 3: "23", 4: "35"},
                "zipcode": {0: "12345", 1: "23456", 2: "34567", 3: "12345", 4: "23456"},
                "gender": {0: "gendered", 1: "gendered", 2: "gendered", 3: "gendered", 4: "gendered"},
                "city": {0: 0, 1: 0, 2: 1, 3: 1, 4: 2},
                "income": {0: "high", 1: "medium", 2: "low", 3: "medium", 4: "low"},
            }
        )
        self.assertEqual(self.anonymizeData.partitions, [])
        self.anonymizeData.anonymize_partition(self.anonymizeData.data.inputData)
        self.assertTrue(self.anonymizeData.partitions[0].equals(expected))

    def test_generalize_partitions(self):
        expected = pd.DataFrame(
            {
                "name": {0: "*", 1: "*", 2: "*", 3: "*", 4: "*"},
                "age": {0: "23#45", 1: "23#45", 2: "23#45", 3: "23#45", 4: "23#45"},
                "zipcode": {0: "12345#34567", 1: "12345#34567", 2: "12345#34567", 3: "12345#34567", 4: "12345#34567"},
                "gender": {0: "gendered", 1: "gendered", 2: "gendered", 3: "gendered", 4: "gendered"},
                "city": {
                    0: "berlin#frankfurt#stuttgart",
                    1: "berlin#frankfurt#stuttgart",
                    2: "berlin#frankfurt#stuttgart",
                    3: "berlin#frankfurt#stuttgart",
                    4: "berlin#frankfurt#stuttgart",
                },
                "income": {0: "high", 1: "medium", 2: "low", 3: "medium", 4: "low"},
            }
        )
        self.anonymizeData.anonymize_partition(self.anonymizeData.data.inputData)
        self.anonymizeData.generalize_partitions()
        self.assertTrue(self.anonymizeData.partitions[0].equals(expected))

    def test_split_partition(self):
        self.assertIsNone(self.anonymizeData.split_partition(self.anonymizeData.data.inputData, "age", "35"))

        anonymizeData = KAnonymityAnonymizer(1, self.data)
        expected_left = pd.DataFrame(
            {
                "name": {0: "Christian", 1: "D", 3: "E", 4: "F"},
                "age": {0: "23", 1: "35", 3: "23", 4: "35"},
                "zipcode": {0: "12345", 1: "23456", 3: "12345", 4: "23456"},
                "gender": {0: "male", 1: "female", 3: "female", 4: "male"},
                "city": {0: "Berlin", 1: "berlin", 3: "frankFurt", 4: "Stuttgart"},
                "income": {0: "high", 1: "medium", 3: "medium", 4: "low"},
            }
        )
        expected_right = pd.DataFrame(
            {
                "name": {2: "C"},
                "age": {2: "45"},
                "zipcode": {2: "34567"},
                "gender": {2: "female"},
                "city": {2: "Frankfurt"},
                "income": {2: "low"},
            },
        )

        left, right = anonymizeData.split_partition(getInputData(), "age", "35")
        self.assertTrue(left.equals(expected_left) and right.equals(expected_right))

    def test_select_dimension_for_split(self):
        self.assertEqual(self.anonymizeData.select_dimension_for_split(1), "zipcode")

    def test_anonymize(self):
        self.anonymizeData.anonymize()
        expected_dataframe = pd.DataFrame(
            {
                "name": ["*"] * 5,
                "age": ["23#45"] * 5,
                "zipcode": ["12345#34567"] * 5,
                "gender": ["gendered"] * 5,
                "city": ["berlin#frankfurt#stuttgart"] * 5,
                "income": ["high", "medium", "low", "medium", "low"],
            }
        )

        self.assertTrue(self.anonymizeData.partitions[0].equals(expected_dataframe))


class TestEpsilonAnonymizer(unittest.TestCase):
    def setUp(self):
        self.data = EpsilonData(getInputData(), getQuasiIdentfiersEpsilon())
        self.anonymizeData = EpsilonAnonymizer(0.1, self.data)

    def test_anonymize(self):
        self.anonymizeData.anonymize()
        self.assertEqual(self.anonymizeData.data.histogram.shape, (3, 3, 5, 2))

    def test_geometric_algorithm(self): ...
