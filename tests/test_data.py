import json
import unittest

import numpy as np
import pandas as pd

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


class TestKData(unittest.TestCase):
    def test_can_categorize(self):
        self.data = KAnonymityData(getInputData(), getQuasiIdentifiersK(), getIdentifiers())
        self.assertEqual(KAnonymityData._can_categorize(self.data, "name"), True)
        self.assertEqual(KAnonymityData._can_categorize(self.data, "age"), None)
        self.assertEqual(KAnonymityData._can_categorize(self.data, "zipcode"), None)
        self.assertEqual(KAnonymityData._can_categorize(self.data, "gender"), True)
        self.assertEqual(KAnonymityData._can_categorize(self.data, "city"), False)
        self.assertEqual(KAnonymityData._can_categorize(self.data, "income"), True)

    def test_prepare(self):
        self.data = KAnonymityData(getInputData(), getQuasiIdentifiersK(), getIdentifiers())
        expected_name = pd.DataFrame({"name": ["*", "*", "*", "*", "*"]})
        expected_age = self.data.inputData["age"]
        expected_zipcode = self.data.inputData["zipcode"]
        expected_gender = pd.DataFrame({"gender": ["gendered", "gendered", "gendered", "gendered", "gendered"]})
        expected_city = pd.DataFrame({"city": [0, 0, 1, 1, 2]})
        expected_income = self.data.inputData["income"]

        KAnonymityData._prepare(self.data, getQuasiIdentifiersK())

        self.assertTrue(self.data.inputData["name"].equals(expected_name["name"]))
        self.assertTrue(self.data.inputData["age"].equals(expected_age))
        self.assertTrue(self.data.inputData["zipcode"].equals(expected_zipcode))
        self.assertTrue(self.data.inputData["gender"].equals(expected_gender["gender"]))
        self.assertTrue(self.data.inputData["city"].equals(expected_city["city"]))
        self.assertTrue(self.data.inputData["income"].equals(expected_income))

    def test_anonymize_identifiers(self):
        self.data = KAnonymityData(getInputData(), getQuasiIdentifiersK(), getIdentifiers())

        expected_identifier = pd.DataFrame({"name": ["*", "*", "*", "*", "*"]})
        self.assertTrue(self.data.inputData["name"].equals(expected_identifier["name"]))


class TestEpsilonData(unittest.TestCase):
    def test_histogram_shape(self):
        self.data = EpsilonData(getInputData(), getQuasiIdentfiersEpsilon())
        expected_shape = [getInputData()[col].nunique() for col in getQuasiIdentfiersEpsilon()]
        self.assertEqual(self.data.histogram.shape, tuple(expected_shape))

    def test_histogram_content(self):
        self.data = EpsilonData(getInputData(), getQuasiIdentfiersEpsilon())
        expected_histogram = [
            [
                [[1, 0], [0, 0], [0, 0], [0, 1], [0, 0]],
                [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            ],
            [
                [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                [[0, 0], [0, 1], [0, 0], [0, 0], [1, 0]],
                [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
            ],
            [
                [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                [[0, 0], [0, 0], [0, 1], [0, 0], [0, 0]],
            ],
        ]
        self.maxDiff = None
        self.assertListEqual(expected_histogram, self.data.histogram.tolist())
