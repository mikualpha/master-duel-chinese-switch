from functools import reduce
from typing import Callable

from tqdm import tqdm
from tqdm.contrib import tenumerate

from api import api, api_local, CacheManager
from hint import CardRawData, CardRawDataItem


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
    p_effect = desc[p_start + 1 : cn_separator_start - 1].strip()
    monster_effect = desc[cn_separator_start + len(ch_separator) :].strip()

    res = ""
    res += monster_effect
    if p_effect != "":
        res = f"{res}\n{separator}\n{p_effect}"

    return res


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


def unity(desc: str) -> str:
    return unify_separator(unify_pendulum_desc(desc))


if __name__ == "__main__":
    # 测试
    print(
        [
            unify_separator(
                unify_pendulum_desc(
                    """
        ①：1回合1次，可以从以下效果选择1个发动。\r\n●以自己场上1只「X-首领加农」为对象，把这张卡当作装备卡使用给那只怪兽装备。装备怪兽被战斗・效果破坏的场合，作为代替把这张卡破坏。\r\n●装备的这张卡特殊召唤。\r\n【灵摆效果】\r\n①：装备怪兽的攻击力・守备力上升400。
        """
                )
            )
        ]
    )
    print([unify_separator("①：1回合1次，可以从以下效果选择1个发动。\r\n●以自己场上1只「X-首领加农」为对象，把这张卡当作装备卡使用给那只怪兽装备。装备怪兽被战斗・效果破坏的场合，作为代替把这张卡破坏。\r\n●装备的这张卡特殊召唤。\r\n【灵摆效果】\r\n②：装备怪兽的攻击力・守备力上升400。")])
    print([unify_separator("①：1回合1次，可以从以下效果选择1个发动。\r\n●以自己场上1只「X-首领加农」为对象，把这张卡当作装备卡使用给那只怪兽装备。装备怪兽被战斗・效果破坏的场合，作为代替把这张卡破坏。\r\n●装备的这张卡特殊召唤。\r\n②：装备怪兽的攻击力・守备力上升400。●装备的这张卡特殊召唤。\r\n\r\n③：装备怪兽的攻击力・守备力上升400。")])


def card_translate(
    archived_Data: CardRawData,
    card_raw_data: CardRawData,
    progress_update_cb: Callable[[str], None] = lambda _: None,
    network_error_cb: Callable[[], None] = lambda: None,
    dev_mode: bool = False,
) -> CardRawData:

    # 统计同名卡的函数
    # card_name = {}
    # def stat_repeat_card_name(name_md: str, desc_md: str):
    #     if name_md not in card_name:
    #         card_name[name_md] = desc_md
    #     elif desc_md == card_name[name_md]:
    #         pass
    #     else:
    #         success = 0
    #         for x in archived_Data:
    #             if x["name"]["zh-cn"] == name_md:
    #                 if x["desc"]["zh-cn"] == desc_md:
    #                     success += 1
    #                 elif x["desc"]["zh-cn"] == card_name[name_md]:
    #                     success += 1
    #
    #                 if success >= 2:
    #                     print('Need Add to list:', name_md)
    #                     break
    #
    #         if success < 2:
    #             print('Error:', name_md, "\n", desc_md, "\n", card_name[name_md])
    #             print('')

    # 某些日文不同卡名但中文翻译翻成同卡名的玩意
    special_card_name = {'礼品卡', '魔法神灯', '骷髅骑士', '混沌巫师', '暴风雨', '核心爆裂', '流星龙',
                         '宝贝龙', '磁力戒指', '补给部队', '扰乱怪衍生物', '契约履行'}

    def search_archived_data(name_cn: str, desc_cn: str) -> CardRawDataItem | None:
        result_obj = None
        for data_obj in archived_Data:
            if data_obj["name"]["zh-cn"] == name_cn:
                if name_cn not in special_card_name:
                    result_obj = data_obj
                    break
                if data_obj["desc"]["zh-cn"] == desc_cn:  # 某些特殊卡片要二次校验
                    result_obj = data_obj
                    break

        if dev_mode and result_obj is not None:
            CacheManager.add_cache(cid,
                                   jp_name=result_obj.get('name', {}).get('ja-jp', ''),
                                   cn_name=result_obj.get('name', {}).get('custom', ''),
                                   md_name=result_obj.get('name', {}).get('zh-cn', ''),
                                   original_desc=result_obj.get('desc', {}).get('zh-cn', ''),
                                   custom_desc=result_obj.get('desc', {}).get('custom', ''))
        return result_obj

    iterable = (
        tenumerate(card_raw_data)
        if dev_mode
        else enumerate(card_raw_data)
    )

    for i, item in iterable:
        cid = item["cid"]
        name_md = item["name"]["zh-cn"]
        desc_md = item["desc"]["zh-cn"]

        progress_update_cb(f"{i}/{len(card_raw_data)}")
        # 新翻译文件(使用CID查找)
        if result_api_local := api_local(cid):
            # 在本地缓存中找到对应的日文名
            item["name"]["custom"] = result_api_local["name"]
            item["desc"]["custom"] = unity(result_api_local["desc"])
            continue

        if result_api := api(name_md, cid, desc_md, network_error_cb, dev_mode):
            # print('API Remote Found:', name_md, result_api)

            # 在API中找到了对应的日文名
            item["name"]["custom"] = result_api["name"]
            item["desc"]["custom"] = unity(result_api["desc"])  # 修正灵摆...修正\r\n
            continue

        # 旧版翻译文件
        if result_archived := search_archived_data(name_md, desc_md):
            # print('Local JSON Found:', name_md)
            
            # 在已归档数据中找到了对应的日文名
            item["name"]["custom"] = result_archived["name"]["custom"]
            item["desc"]["custom"] = unity(result_archived["desc"]["custom"])
            continue

        # 未找到对应的日文名
        if dev_mode:
            tqdm.write(f"WARN: Can't find {name_md}({cid})")

        item["name"]["custom"] = item["name"]["zh-cn"]
        item["desc"]["custom"] = item["desc"]["zh-cn"]

    return card_raw_data
