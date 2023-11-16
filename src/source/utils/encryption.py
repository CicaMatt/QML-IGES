import binascii
import os
from pathlib import Path
from cryptography.fernet import Fernet


def encrypt(path, key):
    data_directory = Path(path)
    fernet = Fernet(key)

    for root, dirs, files in os.walk(data_directory):
        for file in files:
            if ".dat" in str(file):
                continue
            file_name = os.path.splitext(file)[0]
            file_path = os.path.join(root, file)

            to_encrypt = open(file_path, "rb").read()
            hex_value = binascii.hexlify(to_encrypt)

            # Cifratura dati utente
            encrypted_user_data = fernet.encrypt(hex_value)

            # Salva i dati cifrati nella cartella protetta
            new_file_path = os.path.join(data_directory, file_name + '.dat')
            with open(new_file_path, 'wb') as data:
                data.write(encrypted_user_data)
            os.remove(file_path)


def decrypt(path, key):
    data_directory = Path(path)
    fernet = Fernet(key)

    for root, dirs, files in os.walk(data_directory):
        for file in files:
            if not ".dat" in str(file):
                continue
            file_name = os.path.splitext(file)[0]
            file_path = os.path.join(root, file_name)

            with open(file_path + ".dat", 'rb') as data:
                to_decrypt = data.read()
            decrypted_data = fernet.decrypt(to_decrypt)
            binary_value = binascii.unhexlify(decrypted_data)

            # PNG file
            if "graph" in file_name:
                with open(file_path + '.png', 'wb') as original_file:
                    original_file.write(binary_value)
            # XLSX file
            elif "xlsx" in file_name:
                with open(file_path + '.xlsx', 'wb') as original_file:
                    original_file.write(binary_value)
            # TXT file
            elif "txt" in file_name:
                with open(file_path + '.txt', 'wb') as original_file:
                    original_file.write(binary_value)
            # Model file
            elif "model" in file_name:
                with open(file_path + '.sav', 'wb') as original_file:
                    original_file.write(binary_value)
            # CSV file
            else:
                with open(file_path + '.csv', 'wb') as original_file:
                    original_file.write(binary_value)
