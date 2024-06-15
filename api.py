import json
from os import path
from typing import Callable, Literal, NoReturn, TypedDict, Union
from utils import get_resource_path, q2b_string
from functools import reduce
import requests


NameDesc = TypedDict("Card", {"name": str, "desc": str})


class UnifyChar:
    @staticmethod
    def unify_pendulum_desc(desc: str) -> str:
        """
        统一各种灵摆的格式

        样例：①...\n【灵摆效果】\n①...
        """
        if not desc.startswith("←"):  # 这种判断方式挺粗糙的
            return desc  # 不是灵摆就算了
        separator = "【灵摆效果】"
        ch_separator = "【怪兽效果】"
        if desc.find(ch_separator) == -1:
            ch_separator = "【怪兽描述】"
        if desc.find(ch_separator) == -1:
            ch_separator = "【Monster Effect】"  # 怎么还有英文的啊 这是人能干出来的事吗
        if desc.find(ch_separator) == -1:
            ch_separator = "【Flavor Text】"  # 居然还有这种无比阴间的...

        if desc.find(ch_separator) == -1:
            return desc  # 还是找不到就算了

        p_start = desc.find("→")
        cn_separator_start = desc.find(ch_separator)
        p_effect = desc[p_start + 1: cn_separator_start - 1].strip()
        monster_effect = desc[cn_separator_start + len(ch_separator):].strip()

        res = ""
        res += monster_effect
        if p_effect != "":
            res = f"{res}\n{separator}\n{p_effect}"

        return res

    @staticmethod
    def unify_separator(desc: str) -> str:
        """
        按照原版处理分隔符
        1. ①...\n【灵摆效果】\n①...
        2. 召唤限制\n①
        3. ① ②这些的前面不会有\r\n
        """
        orders_without_first = ["②", "③", "④", "⑤", "⑥", "⑦"]
        ch_separator = "【灵摆效果】"
        for order in ["②", "③", "④", "⑤", "⑥", "⑦"]:
            for prefix in ["\r\n", "\n", "\r"]:
                desc = desc.replace(f"{prefix}{order}", order)
        # 处理①
        for prefix in ["\r\n", "\n", "\r"]:
            desc = desc.replace(f"。{prefix}①", "。①")
        desc = desc.replace("\r\n", "\n").strip()
        # 在●后面紧跟的一个②或者③，它们的前面有\n
        parts: list[str] = [f"{'●' if i else ''}{x}" for i, x in enumerate(desc.split("●"))]
        for part in parts:
            if not part.startswith('●'):
                continue
            index = len(part) - 1
            for order in orders_without_first:
                if (i := part.find(order)) != -1:
                    index = min(index, i)
            if (i := part.find("【灵摆效果】")) != -1:
                index = min(index, i)
            if index != len(part) - 1 and part[index] != ch_separator[0]:
                parts[parts.index(part)] = f"{part[:index]}\n{part[index:]}"
        # merge parts
        return reduce(lambda x, y: f"{x}{y}", parts)

    @staticmethod
    def unity(desc: str) -> str:
        return UnifyChar.unify_separator(UnifyChar.unify_pendulum_desc(desc))


class CardsCache(TypedDict):
    name: dict[Literal["jp_name", "cn_name", "md_name"], str]
    desc: dict[Literal["zh-cn", "custom"], str]


class CacheManager(object):
    CACHE_FILE_NAME = 'card_api_cache.json'
    ABNORMAL_CARD_START_ID = 30000  # 似乎是临时卡片，不加进缓存先
    cardCache: dict[str, CardsCache] = {}

    @classmethod
    def add_cache(cls, cid: int, jp_name: str = '', cn_name: str = '',
                  md_name: str = '', original_desc: str = '', custom_desc: str = ''):
        if cid >= cls.ABNORMAL_CARD_START_ID:
            print('Temporary card, skip save:', cid, md_name, cn_name)
            return

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
        print('Add Cache:', cid, md_name, '->', cn_name, len(cls.cardCache))
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

            # if dev_mode:  # 刷新一下游戏内翻译
            #     CacheManager.add_cache(cid,
            #                            jp_name=x['name']['jp_name'],
            #                            cn_name=x['name']['cn_name'],
            #                            md_name=name_md,
            #                            original_desc=desc_md,
            #                            custom_desc=x['desc']['custom'])

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
        search: str, cid: int, desc_src: str, network_error_cb: Callable[[], None] = lambda: None,
        dev_mode: bool = False,
) -> Union[NameDesc, None, NoReturn]:
    if not search:  # 没卡名查什么- -
        return None

    if search.endswith("衍生物"):
        return None  # YGOCDB不收录衍生物

    # 全角转半角
    # search = q2b_string(search)
    search = search.replace(' ', ' ')  # 处理NBSP空格问题

    def helper(search_keyword: str) -> Union[NameDesc, None, NoReturn]:
        url = "https://ygocdb.com/api/v0/?search="
        r = requests.get(url + search_keyword)
        if r.status_code != 200:
            raise ConnectionError()
        result = r.json()["result"]
        if len(result) == 0:
            return None  # 找不到 直接返回 None

        item = None
        for card_item in result:
            if card_item["cid"] == cid or card_item["md_name"] == search:
                item = card_item
                break

        if not item:
            return None

        name: str = item["cn_name"]
        desc: str = item["text"]["desc"]
        if (p_desc := item["text"]["pdesc"]) != "":
            desc = f"{desc}\n【灵摆效果】\n{p_desc}"

        desc = UnifyChar.unity(desc)  # 修正灵摆...修正\r\n
        if dev_mode:
            CacheManager.add_cache(cid,
                                   jp_name=item.get('jp_name', ''),
                                   cn_name=item.get('cn_name', ''),
                                   md_name=item.get('md_name', ''),
                                   original_desc=desc_src,
                                   custom_desc=desc)
        return {"name": name, "desc": desc}

    try:
        result = helper(str(cid))
        if not result:
            result = helper(search)
        return result
    except Exception as e:
        try:
            return helper(search)
        except:
            network_error_cb()
            return None


if __name__ == "__main__":
    # 测试
    print(
        [
            UnityChar.unify_separator(
                UnityChar.unify_pendulum_desc(
                    """
        ①：1回合1次，可以从以下效果选择1个发动。\r\n●以自己场上1只「X-首领加农」为对象，把这张卡当作装备卡使用给那只怪兽装备。装备怪兽被战斗・效果破坏的场合，作为代替把这张卡破坏。\r\n●装备的这张卡特殊召唤。\r\n【灵摆效果】\r\n①：装备怪兽的攻击力・守备力上升400。
        """
                )
            )
        ]
    )
    print([UnityChar.unify_separator(
        "①：1回合1次，可以从以下效果选择1个发动。\r\n●以自己场上1只「X-首领加农」为对象，把这张卡当作装备卡使用给那只怪兽装备。装备怪兽被战斗・效果破坏的场合，作为代替把这张卡破坏。\r\n●装备的这张卡特殊召唤。\r\n【灵摆效果】\r\n②：装备怪兽的攻击力・守备力上升400。")])
    print([UnityChar.unify_separator(
        "①：1回合1次，可以从以下效果选择1个发动。\r\n●以自己场上1只「X-首领加农」为对象，把这张卡当作装备卡使用给那只怪兽装备。装备怪兽被战斗・效果破坏的场合，作为代替把这张卡破坏。\r\n●装备的这张卡特殊召唤。\r\n②：装备怪兽的攻击力・守备力上升400。●装备的这张卡特殊召唤。\r\n\r\n③：装备怪兽的攻击力・守备力上升400。")])
