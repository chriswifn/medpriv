import json
import os
import unittest

from medpriv.config import BaseConfig, ConfigLoader, EpsilonConfig, KConfig, config
from medpriv.utils import File

k_config_data = KConfig(
    k=10,
    identifiers=["name"],
    quasiIdentifiers=["age", "gender"],
    inputFile=File("input.csv"),
    outputFile=File("output.csv"),
)

epsilon_config_data = EpsilonConfig(
    epsilon=0.1,
    identifiers=["name"],
    quasiIdentifiers=["age", "gender"],
    inputFile=File("input.csv"),
    outputFile=File("output.csv"),
)


class TestKConfig(unittest.TestCase):
    def setUp(self):
        self.cfgFile = File("tests/config_k.json")
        self.cfgLoader = ConfigLoader(self.cfgFile)

    def test_get_k(self):
        self.cfg = self.cfgLoader.load_config()
        self.assertEqual(self.cfg.k, 10)

    def test_get_identifiers(self):
        self.cfg = self.cfgLoader.load_config()
        self.assertEqual(self.cfg.identifiers, ["name"])

    def test_get_quasiIdentifiers(self):
        self.cfg = self.cfgLoader.load_config()
        self.assertEqual(self.cfg.quasiIdentifiers, ["age", "gender"])

    def test_get_inputFile(self):
        self.cfg = self.cfgLoader.load_config()
        expected_inputFile: File = File("input.csv")
        self.assertEqual(self.cfg.inputFile.to_dict().lower(), expected_inputFile.to_dict().lower())

    def test_get_outputFile(self):
        self.cfg = self.cfgLoader.load_config()
        excepted_outputFile: File = File("output.csv")
        self.assertEqual(self.cfg.outputFile.to_dict().lower(), excepted_outputFile.to_dict().lower())


class TestEpsilonConfig(unittest.TestCase):
    def setUp(self):
        self.cfgFile = File("tests/config_epsilon.json")
        self.cfgLoader = ConfigLoader(self.cfgFile)

    def test_get_epsilon(self):
        self.cfg = self.cfgLoader.load_config()
        self.assertEqual(self.cfg.epsilon, 0.1)

    def test_get_identifiers(self):
        self.cfg = self.cfgLoader.load_config()
        self.assertEqual(self.cfg.identifiers, ["name"])

    def test_get_quasiIdentifiers(self):
        self.cfg = self.cfgLoader.load_config()
        self.assertEqual(self.cfg.quasiIdentifiers, ["age", "gender"])

    def test_get_inputFile(self):
        self.cfg = self.cfgLoader.load_config()
        expected_inputFile: File = File("input.csv")
        self.assertEqual(self.cfg.inputFile.to_dict().lower(), expected_inputFile.to_dict().lower())

    def test_get_outputFile(self):
        self.cfg = self.cfgLoader.load_config()
        excepted_outputFile: File = File("output.csv")
        self.assertEqual(self.cfg.outputFile.to_dict().lower(), excepted_outputFile.to_dict().lower())


class TestBaseConfig(unittest.TestCase):
    def setUp(self):
        self.cfg = BaseConfig(
            k_config_data.identifiers, k_config_data.quasiIdentifiers, k_config_data.inputFile, k_config_data.outputFile
        )

    def test_to_dict(self):
        expected_dict = {
            "identifiers": ["name"],
            "quasiIdentifiers": ["age", "gender"],
            "inputFile": File("input.csv").to_dict(),
            "outputFile": File("output.csv").to_dict(),
        }
        self.assertEqual(self.cfg.to_dict(), expected_dict)

    def test_from_dict(self):
        k_dict = {
            "identifiers": ["name"],
            "quasiIdentifiers": ["age", "gender"],
            "inputFile": File("input.csv").to_dict(),
            "outputFile": File("output.csv").to_dict(),
            "k": 10,
        }
        k_config = KConfig.from_dict(k_dict)
        self.assertIsInstance(k_config, KConfig)
        self.assertEqual(k_config.identifiers, k_dict["identifiers"])
        self.assertEqual(k_config.quasiIdentifiers, k_dict["quasiIdentifiers"])
        self.assertEqual(k_config.k, k_dict["k"])

        epsilon_dict = {
            "identifiers": ["name"],
            "quasiIdentifiers": ["age", "gender"],
            "inputFile": File("input.csv").to_dict(),
            "outputFile": File("output.csv").to_dict(),
            "epsilon": 0.1,
        }
        epsilon_config = EpsilonConfig.from_dict(epsilon_dict)
        self.assertIsInstance(epsilon_config, EpsilonConfig)
        self.assertEqual(epsilon_config.identifiers, epsilon_dict["identifiers"])
        self.assertEqual(epsilon_config.quasiIdentifiers, epsilon_dict["quasiIdentifiers"])
        self.assertEqual(epsilon_config.epsilon, epsilon_dict["epsilon"])


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.cfgFile = File("tests/config_k.json")
        self.cfgLoader = ConfigLoader(self.cfgFile)

    def test_load_config(self):
        config = self.cfgLoader.load_config()
        expected_config = KConfig(
            ["name"],
            ["age", "gender"],
            File("input.csv"),
            File("output.csv"),
            10,
        )

        self.assertListEqual(config.identifiers, expected_config.identifiers)
        self.assertListEqual(config.quasiIdentifiers, expected_config.quasiIdentifiers)
        self.assertEqual(config.inputFile.to_dict().lower(), expected_config.inputFile.to_dict().lower())
        self.assertEqual(config.outputFile.to_dict().lower(), expected_config.outputFile.to_dict().lower())
        self.assertEqual(config.k, expected_config.k)

    def test_FileNotFound(self):
        self.cfgFile = File("configTest.json")
        self.cfgLoader = ConfigLoader(self.cfgFile)
        with self.assertRaises(FileNotFoundError):
            self.cfgLoader.load_config()

    def test_JSONDecodeError(self):
        self.cfgFile = File("tests/invalidConfig.json")
        self.cfgLoader = ConfigLoader(self.cfgFile)
        with self.assertRaises(ValueError):
            self.cfgLoader.load_config()

    def test_dict_to_config(self):
        k_dict = {
            "identifiers": ["name"],
            "quasiIdentifiers": ["age", "gender"],
            "inputFile": File("input.csv").to_dict(),
            "outputFile": File("output.csv").to_dict(),
            "k": 10,
        }
        epsilon_dict = {
            "identifiers": ["name"],
            "quasiIdentifiers": ["age", "gender"],
            "inputFile": File("input.csv").to_dict(),
            "outputFile": File("output.csv").to_dict(),
            "epsilon": 10,
        }

        self.assertIsInstance(self.cfgLoader._dict_to_config(k_dict), KConfig)
        self.assertIsInstance(self.cfgLoader._dict_to_config(epsilon_dict), EpsilonConfig)
        with self.assertRaises(ValueError):
            self.cfgLoader._dict_to_config({})

    def test_init_config(self):
        defaultConfig = KConfig(
            k=3,
            identifiers=["name"],
            quasiIdentifiers=["age", "gender"],
            inputFile=File("input.csv"),
            outputFile=File("output.csv"),
        )

        name = "dummy.json"
        self.cfgLoader.configFile = File(name)
        self.cfgLoader.init_config(defaultConfig)
        self.assertTrue(os.path.isfile(name))
        os.remove(name)
