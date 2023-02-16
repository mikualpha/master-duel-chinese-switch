from tqdm import tqdm
from hint import CardRawData, CardRawDataItem
from api import api, api_local
from typing import Callable
from tqdm.contrib import tenumerate


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
    for key_word in ["②", "③", "④", "⑤", "⑥", "⑦"]:
        for prefix in ["\r\n", "\n", "\r"]:
            desc = desc.replace(f"{prefix}{key_word}", key_word)
    # 处理①
    for prefix in ["\r\n", "\n", "\r"]:
        desc = desc.replace(f"。{prefix}①", "。①")
    return desc.replace("\r\n", "\n").strip()


def unity(desc: str) -> str:
    return unify_separator(unify_pendulum_desc(desc))


if __name__ == "__main__":
    # 测试
    print(
        [
            unify_separator(
                unify_pendulum_desc(
                    """
        这张卡不能特殊召唤。这张卡通常召唤的场合，必须把3只解放作召唤。\r\n①：这张卡的召唤不会被无效化。\r\n②：在这张卡的召唤成功时，这张卡以外的魔法・陷阱・怪兽的效果不能发动。\r\n③：这张卡召唤成功时，把基本分支付到变成100基本分才能发动。这张卡的攻击力・守备力上升支付的数值。\r\n④：支付1000基本分，以场上1只怪兽为对象才能发动。那只怪兽破坏。
        """
                )
            )
        ]
    )


def card_translate(
    archived_Data: CardRawData,
    card_raw_data: CardRawData,
    progress_update_cb: Callable[[str], None] = lambda _: None,
    network_error_cb: Callable[[], None] = lambda: None,
    dev_mode: bool = False,
) -> CardRawData:
    def search_archived_data(name_jp: str) -> CardRawDataItem | None:
        for item in archived_Data:
            if item["name"]["ja-jp"] == name_jp:
                return item
        return None

    iterable = (
        tenumerate(card_raw_data)
        if dev_mode
        else enumerate(card_raw_data)
    )

    for i, item in iterable:
        name_jp = item["name"]["ja-jp"]
        progress_update_cb(f"{i}/{len(card_raw_data)}")
        if result_archived:= search_archived_data(name_jp):
            # 在已归档数据中找到了对应的日文名
            item["name"]["custom"] = result_archived["name"]["custom"]
            item["desc"]["custom"] = unity(result_archived["desc"]["custom"])
            continue
        if result_api_local:= api_local(name_jp):
            # 在本地API中找到了对应的日文名
            item["name"]["custom"] = result_api_local["name"]
            item["desc"]["custom"] = unity(result_api_local["desc"])
        if result_api:= api(name_jp, network_error_cb):
            # 在API中找到了对应的日文名
            item["name"]["custom"] = result_api["name"]
            item["desc"]["custom"] = unity(result_api["desc"])  # 修正灵摆...修正\r\n
            continue
        # 未找到对应的日文名
        if dev_mode:
            tqdm.write(f"Can't find {name_jp}")
        item["name"]["custom"] = item["name"]["zh-cn"]
        item["desc"]["custom"] = item["desc"]["zh-cn"]

    return card_raw_data
