import os
from typing import Any
import shutil
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
    file_path_list = getFilesList(dir_input)

    for file in file_path_list:
        src_file = os.path.join(dir_input, file[:2], file)
        dst_file = os.path.join(dir_output, file[:2], file)
        createFolder(os.path.join(dir_output, file[:2]))
        # shutil.copyfile(src_file, dst_file)

        env = UnityPy.load(src_file)
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                data: Any = obj.read()
                name: str = data.name.upper()
                if name in ["CARD_PROP"]:  # 不需要保存ID文件(没有修改)
                    continue
                data.script = card_encrypt_data[name.replace('RUBY', '')]
                data.save()

        with open(os.path.join(dst_file), "wb") as f:
            f.write(env.file.save())
