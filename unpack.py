from typing import Any, cast

import UnityPy

from hint import CardData, PathIdDict
from utils import getFilesList


def card_unpack(path_data_unity3d: dict[str, str]) -> CardData:
    result: CardData = cast(CardData, {"ja-jp": {}, "zh-cn": {}})
    for obj_name, obj_path in path_data_unity3d.items():
        env = UnityPy.load(obj_path)
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                data: Any = obj.read()
                name = data.name.upper()
                result['zh-cn'][name] = bytes(data.script)

    return result
