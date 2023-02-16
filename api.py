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


class CardsBaiGe(TypedDict):
    name: dict[Literal["ja-jp", "nw_name"], str]
    desc: dict[Literal["custom"], str]


def api_local(search: str) -> Union[NameDesc, None]:
    with open(
            path.join(get_resource_path("resources"), "card_baige.json"), encoding="utf-8"
        ) as f:
            cards: list[CardsBaiGe] = json.load(f)
    def helper(search: str) -> Union[NameDesc, None]:
        if search in [x["name"]["ja-jp"] for x in cards]:
            return {
                "name": [
                    x["name"]["nw_name"] for x in cards if x["name"]["ja-jp"] == search
                ][0],
                "desc": [
                    x["desc"]["custom"] for x in cards if x["name"]["ja-jp"] == search
                ][0],
            }
        else:
            return None
    try:
        if q2b_res := helper(q2b_string(search)):
            return q2b_res
        return helper(search)
    except:
        return None


def api(
    search: str, network_error_cb: Callable[[], None] = lambda: None
) -> Union[NameDesc, None, NoReturn]:
    # 全角转半角
    search = q2b_string(search)

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
        p_desc: str = item["text"]["pdesc"]
        if p_desc != "":
            desc = f"{desc}\n【灵摆效果】\n{p_desc}"
        return {"name": name, "desc": desc}

    try:
        return helper(search)
    except:
        # 出错重试
        try:
            return helper(search)
        except:
            network_error_cb()
            return None


if __name__ == "__main__":
    print(api_local("D-HERO ドミネイトガイ"))
    print(q2b_string("魔神儀の創造主－クリオルター"))
