import os
from pathlib import Path
from cryptography.fernet import Fernet


def encrypt(path, key):
    data_directory = Path(path)
    fernet = Fernet(key)

    for root, dirs, files in os.walk(data_directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = str(file)[:-4]

            to_encrypt = open(file_path, "r")

            # Cifratura dati utente
            encrypted_user_data = fernet.encrypt(str(to_encrypt).encode())

            # Salva i dati cifrati nella cartella protetta
            new_file_path = os.path.join(data_directory, file_name + '.dat')
            with open(new_file_path, 'wb') as file:
                file.write(encrypted_user_data)
            os.remove(file_path)


def decrypt(path, key):
    data_directory = Path(path)
    fernet = Fernet(key)

    for root, dirs, files in os.walk(data_directory):
        for file in files:
            file_name = str(file)[:-4]
            file_path = root / file_name

            encrypted_data = file.read()
            decrypted_data = fernet.decrypt(encrypted_data)

            # PNG file
            if "graph" in file_name:
                with open(file_path + '.png', 'wb') as original_file:
                    original_file.write(decrypted_data)
            # XLSX file
            elif "xlsx" in file_name:
                with open(file_path + '.xlsx', 'wb') as original_file:
                    original_file.write(decrypted_data)
            # TXT file
            elif "txt" in file_name:
                with open(file_path + '.txt', 'wb') as original_file:
                    original_file.write(decrypted_data)
            # CSV file
            else:
                # transformed_data = (str(decrypted_data)[2:-1]).replace('\\t', ',').replace('\\n', '\n')
                with open(file_path + '.csv', 'wb') as original_file:
                    original_file.write(decrypted_data)
