import os
import time


def delete_zip(path):
    time.sleep(1)
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == ".zip":
                os.remove(path / file)
