import os
from typing import Any
import UnityPy

from hint import CardEncryptedData
from move import create_folder


def card_pack(card_encrypt_data: CardEncryptedData, dir_input: str, dir_output: str, file_list: dict[str, str]):
    for file_type, file in file_list.items():
        src_file = os.path.join(dir_input, file[:2], file)
        dst_file = os.path.join(dir_output, file[:2], file)

        if not os.path.exists(src_file):  # 文件不存在
            continue

        if file_type in ("CARD_Prop", ):  # 不需要保存ID文件(没有修改)
            continue

        env = UnityPy.load(src_file)
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                data: Any = obj.read()
                name: str = data.name.upper()
                data.script = card_encrypt_data[name.replace('RUBY', '')]
                data.save()

        create_folder(os.path.join(dir_output, file[:2]))
        with open(os.path.join(dst_file), "wb") as f:
            f.write(env.file.save())
