from typing import Any, cast

import UnityPy

from hint import CardData, PathIdDict
from utils import getFilesList

# path_id_dict: PathIdDict = {"ja-jp": {}, "zh-cn": {}}

obj_name_list = [
    "CARD_INDX",
    "CARD_NAME",
    "CARD_DESC",
    "CARD_PART",  # 这两玩意是卡片做了一个拆
    "CARD_PIDX",
]


def to_UPPER_CASE(s: str) -> str:
    a, b = s.split("_")
    return f"{a.upper()}_{b.upper()}"


# def gen_path_id_map(env: UnityPy.Environment):
#     for obj in env.objects:
#         if obj.type.name == "ResourceManager":
#             rm: Any = obj.read()
#             for container, ptr in rm.m_Container.items():
#                 try:
#                     data = ptr.read()
#                     path_id = data.path_id
#                     if len(container.split("/")[-2:]) < 2:
#                         continue
#                     lang, _obj_name = container.split("/")[-2:]
#                     if lang in path_id_dict.keys() and _obj_name in [
#                         x.lower() for x in obj_name_list
#                     ]:  # ! 这儿_obj_name是小写的...
#                         path_id_dict[lang][path_id] = to_UPPER_CASE(_obj_name)
#                 except Exception:
#                     ...
#             break


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
