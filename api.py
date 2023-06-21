import json
import hashlib
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
    name: dict[Literal["jp_name", "cn_name", "en_name", "jp_ruby",
                       "nw_name", "sc_name", "md_name", "cnocg_n", "nwbbs_n"], str]
    desc: dict[Literal["custom"], str]


class CacheManager(object):
    CACHE_FILE_NAME = 'card_api_cache.json'
    cardCache: dict[str, CardsCache] = {}

    @classmethod
    def add_cache(cls, card_id: int, jp_name: str = '', cn_name: str = '', en_name: str = '', jp_ruby: str = '',
                  nw_name: str = '', sc_name: str = '', md_name: str = '', cnocg_n: str = '', nwbbs_n: str = '',
                  original_desc: str = '', custom_desc: str = ''):
        cache_obj = {
            "id": card_id,
            "name": {
                    "jp_name": jp_name,
                    "cn_name": cn_name,
                    "en_name": en_name,
                    "jp_ruby": jp_ruby,
                    "nw_name": nw_name,
                    "sc_name": sc_name,
                    "md_name": md_name,
                    "cnocg_n": cnocg_n,
                    "nwbbs_n": nwbbs_n
            },
            "desc": {
                "zh-cn": original_desc,
                "custom": custom_desc
            }
        }

        name_hash = hashlib.sha1(md_name.strip().encode('utf-8')).hexdigest()
        cls.cardCache[name_hash] = cache_obj
        # print('Add Cache:', md_name, name_hash, len(cls.cardCache))
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


def api_local(search: str) -> Union[NameDesc, None]:
    cards: dict[str, CardsCache] = CacheManager.load_cache()

    def helper(search: str) -> Union[NameDesc, None]:
        search_hash = hashlib.sha1(search.encode('utf-8')).hexdigest()
        if search_hash in cards:
            x: CardsCache = cards.get(search_hash, None)
            if x is None:
                return None

            return {
                "name": x["name"]["cn_name"],
                "desc": x["desc"]["custom"],
            }
        else:
            return None
    try:
        search = search.replace(' ', ' ')  # 处理NBSP空格问题
        # if q2b_res := helper(q2b_string(search)):
        #     return q2b_res
        return helper(search.strip())
    except Exception as e:
        # raise e
        return None


def api(
    search: str, desc_src: str, network_error_cb: Callable[[], None] = lambda: None, dev_mode: bool = False,
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
            CacheManager.add_cache(item.get("id", -1),
                                   jp_name=item.get('jp_name', ''),
                                   cn_name=item.get('cn_name', ''),
                                   en_name=item.get('en_name', ''),
                                   jp_ruby=item.get('jp_ruby', ''),
                                   nw_name=item.get('nw_name', ''),
                                   sc_name=item.get('sc_name', ''),
                                   md_name=item.get('md_name', ''),
                                   cnocg_n=item.get('cnocg_n', ''),
                                   nwbbs_n=item.get('nwbbs_n', ''),
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
