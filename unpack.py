from typing import Any, cast

import UnityPy

from hint import CardData, PathIdDict
from utils import getFilesList

path_id_dict: PathIdDict = {"ja-jp": {}, "zh-cn": {}}

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


def gen_path_id_map(env: UnityPy.Environment):
    for obj in env.objects:
        if obj.type.name == "ResourceManager":
            rm: Any = obj.read()
            for container, ptr in rm.m_Container.items():
                try:
                    data = ptr.read()
                    path_id = data.path_id
                    if len(container.split("/")[-2:]) < 2:
                        continue
                    lang, _obj_name = container.split("/")[-2:]
                    if lang in path_id_dict.keys() and _obj_name in [
                        x.lower() for x in obj_name_list
                    ]:  # ! 这儿_obj_name是小写的...
                        path_id_dict[lang][path_id] = to_UPPER_CASE(_obj_name)
                except Exception:
                    ...
            break


def card_unpack(path_data_unity3d: str) -> CardData:
    env = UnityPy.load(path_data_unity3d)
    gen_path_id_map(env)
    result: CardData = cast(CardData, {"ja-jp": {}, "zh-cn": {}})
    for lang in path_id_dict.keys():
        for obj in env.objects:
            if (
                obj.type.name == "TextAsset"
                and obj.path_id in path_id_dict[lang].keys()
            ):
                data: Any = obj.read()
                obj_name: str = path_id_dict[lang][obj.path_id]
                result[lang][obj_name] = bytes(data.script)
    # # -> 从小文件直接读取
    # dir_input = "input"  # 先写死
    # for file in getFilesList(dir_input):
    #     env = UnityPy.load(f"{dir_input}/{file}")
    #     for obj in env.objects:
    #         if obj.type.name == "TextAsset":
    #             data: Any = obj.read()
    #             name = data.name.upper()
    #             result["zh-cn"][name] = bytes(data.script)
    # # <- 从小文件直接读取
    return result
