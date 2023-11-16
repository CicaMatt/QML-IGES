import os
from pathlib import Path
from unittest import TestCase
from src.source.utils.encryption import encrypt, decrypt


class Test_utils(TestCase):

    def setUp(self):
        super().setUp()

    def test_encrypt(self):
        path = Path(__file__).parent / "testingFiles"
        with open(path / "key.txt", 'r') as file:
            key = file.read()
        os.remove(path / "key.txt")

        encrypt(path, key)

        self.assertTrue(Path(path / "csv_file.dat").is_file())
        self.assertTrue(Path(path / "txt_file.dat").is_file())
        self.assertTrue(Path(path / "xlsx_file.dat").is_file())
        self.assertTrue(Path(path / "png_graph.dat").is_file())
        self.assertTrue(Path(path / "model.dat").is_file())

        with open(path / "key.txt", 'w') as file:
            file.write(key)

    def test_decrypt(self):
        path = Path(__file__).parent / "testingFiles"
        with open(path / "key.txt", 'r') as file:
            key = file.read()

        decrypt(path, key)

        self.assertTrue(Path(path / "csv_file.csv").is_file())
        self.assertTrue(Path(path / "txt_file.txt").is_file())
        self.assertTrue(Path(path / "xlsx_file.xlsx").is_file())
        self.assertTrue(Path(path / "png_graph.png").is_file())
        self.assertTrue(Path(path / "model.sav").is_file())

        for root, dirs, files in os.walk(path):
            for file in files:
                if ".dat" in str(file):
                    os.remove(path / file)
