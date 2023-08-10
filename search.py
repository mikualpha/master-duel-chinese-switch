import os
import UnityPy
from typing import Callable


def search_card_obj_list(path_game_root: str, log: Callable[[str], None]) -> dict[str, str]:
    card_obj_name = (
        'CARD_Desc',
        'CARD_Indx',
        'CARD_Name',
        'Card_Part',
        'Card_Pidx',
        'CARD_Prop',
    )

    log("Debug scanning option has been enabled.")
    card_obj_list = {}
    for root, dirs, files in os.walk(os.path.join(path_game_root, 'LocalData')):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                env = UnityPy.load(file_path)
                for obj in env.objects:
                    if obj.type.name == "TextAsset":
                        data = obj.read()
                        name = data.name
                        if name in card_obj_name:
                            if 'zh-cn' not in data.container:  # 不是中文的跳过
                                continue

                            if 'v140' in data.container:  # 忽略旧版本文件
                                continue

                            log("FileName: {}, UnityPath:{}, AssetPath: {}".format(name, data.container, file_path))
                            if name not in card_obj_list:
                                card_obj_list[name] = file
            except Exception as e:
                continue

            if len(card_obj_list) >= len(card_obj_name):
                break

        if len(card_obj_list) >= len(card_obj_name):
            break

    print(repr(card_obj_list))
    return card_obj_list
