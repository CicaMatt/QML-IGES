import os
from pathlib import Path
from unittest import TestCase

from cryptography.fernet import Fernet

from src.source.utils.encryption import encrypt, decrypt
from imageio.v2 import imread


class Test_utils(TestCase):

    def setUp(self):
        super().setUp()

    def test_encrypt(self):
        path = Path(__file__).resolve().parent / "testingFiles"
        with open(path / "key.key", 'r') as file:
            key = file.read()

        encrypt(path, key)

        self.assertTrue(Path(path / "csv_file_clear.dat").is_file())
        self.assertTrue(Path(path / "txt_file_clear.dat").is_file())
        self.assertTrue(Path(path / "xlsx_file_clear.dat").is_file())
        self.assertTrue(Path(path / "png_graph_clear.dat").is_file())
        self.assertTrue(Path(path / "model_clear.dat").is_file())

    def test_decrypt(self):
        path = Path(__file__).resolve().parent / "testingFiles"
        with open(path / "key.key", 'r') as file:
            key = file.read()

        decrypt(path, key)

        self.assertTrue(Path(path / "csv_file_encrypted.csv").is_file())
        self.assertTrue(Path(path / "txt_file_encrypted.txt").is_file())
        self.assertTrue(Path(path / "xlsx_file_encrypted.xlsx").is_file())
        self.assertTrue(Path(path / "png_graph_encrypted.png").is_file())
        self.assertTrue(Path(path / "model_encrypted.sav").is_file())

        self.assertTrue(open(Path(path / "csv_file_encrypted.csv")).read() ==
                        open(Path(path / "csv_file_clear.csv")).read())
        self.assertTrue(open(Path(path / "txt_file_encrypted.txt")).read() ==
                        open(Path(path / "txt_file_clear.txt")).read())
        self.assertTrue(open(Path(path / "xlsx_file_encrypted.xlsx")).read() ==
                        open(Path(path / "xlsx_file_clear.xlsx")).read())
        self.assertTrue((imread(Path(path / "png_graph_encrypted.png")) ==
                        imread(Path(path / "png_graph_clear.png"))).all())
        self.assertTrue(open(Path(path / "model_encrypted.sav")).read() ==
                        open(Path(path / "model_clear.sav")).read())

    def test_encrypt_fail(self):
        path = Path(__file__).resolve().parent / "testingFiles"
        with open(path / "key.key", 'r') as file:
            key = file.read()[10]

        with self.assertRaises(Exception):
            encrypt(path, key)

        self.assertFalse(Path(path / "csv_file_clear.dat").is_file())
        self.assertFalse(Path(path / "txt_file_clear.dat").is_file())
        self.assertFalse(Path(path / "xlsx_file_clear.dat").is_file())
        self.assertFalse(Path(path / "png_graph_clear.dat").is_file())
        self.assertFalse(Path(path / "model_clear.dat").is_file())

    def test_decrypt_fail(self):
        path = Path(__file__).resolve().parent / "testingFiles"
        with open(path / "key.key", 'r') as file:
            key = Fernet.generate_key()

        with self.assertRaises(Exception):
            decrypt(path, key)

        self.assertFalse(Path(path / "csv_file_encrypted.csv").is_file())
        self.assertFalse(Path(path / "txt_file_encrypted.txt").is_file())
        self.assertFalse(Path(path / "xlsx_file_encrypted.xlsx").is_file())
        self.assertFalse(Path(path / "png_graph_encrypted.png").is_file())
        self.assertFalse(Path(path / "model_encrypted.sav").is_file())

    def tearDown(self):
        path = Path(__file__).resolve().parent / "testingFiles"
        for root, dirs, files in os.walk(path):
            for file in files:
                if "clear.dat" in str(file):
                    os.remove(path / file)
                if "encrypted" in str(file) and os.path.splitext(str(file))[1] != ".dat":
                    os.remove(path / file)

