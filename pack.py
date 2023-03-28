import os
from typing import Any

import UnityPy

from hint import CardEncryptedData
from utils import getFilesList


def createFolder(path: str):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)

def card_pack(card_encrypt_data: CardEncryptedData, dir_input: str, dir_output: str):
    for file in getFilesList(dir_input):
        env = UnityPy.load(os.path.join(dir_input, file))
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                data: Any = obj.read()
                name: str = data.name.upper()
                # if name in ["CARD_PIDX"]:
                #     continue
                data.script = card_encrypt_data[name.replace('RUBY', '')]
                data.save()
        createFolder(os.path.join(dir_output, file[:2]))
        with open(os.path.join(dir_output, file[:2], file), "wb") as f:
            f.write(env.file.save())