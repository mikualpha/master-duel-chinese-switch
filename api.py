from typing import Callable, NoReturn, TypedDict, Union

import requests

from utils import q2b_string


def getShortestStrIndex(l: list[str]) -> int:
    shortest = l[0]
    index = 0
    for i, s in enumerate(l):
        if len(s) < len(shortest):
            shortest = s
            index = i
    return index


NameDesc = TypedDict("Card", {"name": str, "desc": str})


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
