import json
from os import path
from typing import Callable, Literal, NoReturn, TypedDict, Union

import requests

from utils import get_resource_path, q2b_string


def getShortestStrIndex(l: list[str]) -> int:
    shortest = l[0]
    index = 0
    for i, s in enumerate(l):
        if len(s) < len(shortest):
            shortest = s
            index = i
    return index


NameDesc = TypedDict("Card", {"name": str, "desc": str})


class CardsCache(TypedDict):
    name: dict[Literal["jp_name", "cn_name", "md_name"], str]
    desc: dict[Literal["zh-cn", "custom"], str]


class CacheManager(object):
    CACHE_FILE_NAME = 'card_api_cache.json'
    cardCache: dict[str, CardsCache] = {}

    @classmethod
    def add_cache(cls, cid: int, jp_name: str = '', cn_name: str = '',
                  md_name: str = '', original_desc: str = '', custom_desc: str = ''):
        cache_obj = {
            "name": {
                "jp_name": jp_name,
                "cn_name": cn_name,
                "md_name": md_name
            },
            "desc": {
                "zh-cn": original_desc,
                "custom": custom_desc
            }
        }

        cls.cardCache[str(cid)] = cache_obj
        print('Add Cache:', cid, md_name, cn_name, len(cls.cardCache))
        cls.save_cache()

    @classmethod
    def save_cache(cls):
        with open(path.join(get_resource_path("resources"), cls.CACHE_FILE_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(cls.cardCache, ensure_ascii=False, separators=(',', ':')))

    @classmethod
    def load_cache(cls) -> dict[str, CardsCache]:
        if len(cls.cardCache) > 0:
            # print('Load Cache: ', len(cls.cardCache))
            return cls.cardCache

        try:
            with open(path.join(get_resource_path("resources"), cls.CACHE_FILE_NAME), encoding="utf-8") as f:
                file_content = f.read().strip()
                if len(file_content) <= 0:
                    return cls.cardCache

                cls.cardCache = json.loads(file_content)
                # print('Load Success: ', len(cls.cardCache))
        except Exception as e:
            cls.cardCache = {}
        return cls.cardCache


def api_local(cid: int) -> Union[NameDesc, None]:
    cards: dict[str, CardsCache] = CacheManager.load_cache()

    def helper(card_id: int) -> Union[NameDesc, None]:
        if str(card_id) in cards:
            x: CardsCache = cards.get(str(card_id), None)
            if x is None:
                return None

            return {
                "name": x["name"]["cn_name"],
                "desc": x["desc"]["custom"],
            }
        else:
            return None

    try:
        return helper(cid)
    except Exception as e:
        # raise e
        return None


def api(
    search: str, cid: int, desc_src: str, network_error_cb: Callable[[], None] = lambda: None, dev_mode: bool = False,
) -> Union[NameDesc, None, NoReturn]:
    if not dev_mode and search.endswith("衍生物"):
        return None  # YGOCDB不收录衍生物

    # 全角转半角
    # search = q2b_string(search)
    search = search.replace(' ', ' ')  # 处理NBSP空格问题

    def helper(search: str) -> Union[NameDesc, None, NoReturn]:
        url = "https://ygocdb.com/api/v0/?search="
        r = requests.get(url + search)
        if r.status_code != 200:
            raise ConnectionError()
        result = r.json()["result"]
        if len(result) == 0:
            return None  # 找不到 直接返回 None
        i = getShortestStrIndex([x["cn_name"] for x in result])
        item = result[i]
        name: str = item["cn_name"]
        desc: str = item["text"]["desc"]
        if (p_desc := item["text"]["pdesc"]) != "":
            desc = f"{desc}\n【灵摆效果】\n{p_desc}"

        if dev_mode:
            CacheManager.add_cache(cid,
                                   jp_name=item.get('jp_name', ''),
                                   cn_name=item.get('cn_name', ''),
                                   md_name=item.get('md_name', ''),
                                   original_desc=desc_src,
                                   custom_desc=desc)
        return {"name": name, "desc": desc}

    try:
        return helper(search)
    except Exception as e:
        # 出错重试
        # raise e
        try:
            return helper(search)
        except:
            network_error_cb()
            return None


if __name__ == "__main__":
    print(api("命运－英雄 统治魔侠"))
    # print(q2b_string("魔神儀の創造主－クリオルター"))
