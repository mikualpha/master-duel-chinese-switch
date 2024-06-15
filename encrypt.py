import re
import zlib
from typing import TypedDict, TypeVar, cast

from hint import CardData, CardEncryptedData, CardRawData
from utils import flatten


class Others(TypedDict):
    CARD_INDX: bytes
    CARD_NAME: bytes
    CARD_DESC: bytes


class PartsOfEachCard(TypedDict):
    slice: list[int]
    parts: list[list[int]]


def gen_others(card_raw_data: CardRawData, m_iCryptoKey: int) -> Others:
    """
    生成 Name Desc Indx
    """
    CARD_Name_json: list[str] = [item["name"]["custom"] for item in card_raw_data]
    CARD_Desc_json: list[str] = [item["desc"]["custom"] for item in card_raw_data]

    merge_string: dict[str, str] = {"name": "\u0000" * 8, "desc": "\u0000" * 8}

    name_indx = [0]
    desc_indx = [0]

    for i in range(len(CARD_Name_json)):  # 这里是因为英语的奇怪bug desc比name少一个
        name = CARD_Name_json[i]
        desc = CARD_Desc_json[i]

        def helper(
            sentence: str,
            indx: list[int],
            name_or_desc: str,
            merge_string: dict[str, str],
        ) -> None:
            length = len(sentence.encode("utf-8"))
            if i == 0:
                length += 8
            space_len = 4 - length % 4  # 就是拿到余数
            indx.append(indx[-1] + length + space_len)  # 记录indx
            if name_or_desc == "name":
                merge_string["name"] += sentence + "\u0000" * space_len
            else:
                merge_string["desc"] += sentence + "\u0000" * space_len

        helper(name, name_indx, "name", merge_string)
        helper(desc, desc_indx, "desc", merge_string)

    name_indx = [4, 8] + name_indx[1:]
    desc_indx = [4, 8] + desc_indx[1:]

    CARD_Indx: list[int] = []
    for i in range(len(name_indx)):
        CARD_Indx.append(name_indx[i])
        CARD_Indx.append(desc_indx[i])

    def intTo4Hex(num: int) -> list[int]:
        res: list[int] = []
        for _ in range(4):
            res.append(num % 256)
            num //= 256
        return res

    CARD_Indx_merge: list[int] = []
    for item in CARD_Indx:
        CARD_Indx_merge.extend(intTo4Hex(item))

    # 直接加密
    result: Others = {"CARD_INDX": bytes(), "CARD_NAME": bytes(), "CARD_DESC": bytes()}
    result["CARD_NAME"] = encrypt(
        m_iCryptoKey, bytes(merge_string["name"], encoding="utf-8")
    )
    result["CARD_DESC"] = encrypt(
        m_iCryptoKey, bytes(merge_string["desc"], encoding="utf-8")
    )
    result["CARD_INDX"] = encrypt(m_iCryptoKey, bytes(CARD_Indx_merge))
    return result


# * part 指的是每张卡的分段，如[0, 100, 100, 200]
# * segment 指的是每张卡的分段后的文本，如["①：...", "②：...", "③：..."]
class CardSegment(TypedDict):
    n_part: int  # 分段数
    is_pendulum: bool  # 是否是灵摆卡
    parts_zh_cn: list[int]  # zh-cn分段 也就是原文分段
    segments_zh_cn: list[str]  # zh-cn分段文本 也就是原文分段文本
    parts_custom: list[int]  # 自定义分段
    segments_custom: list[str]  # 自定义分段文本


class SplitResult(TypedDict):
    n_part: int
    parts: list[int]
    segments: list[str]


def split(desc: str, n_part: int = -1) -> SplitResult:
    starts = [m.start() for m in re.finditer("((①|②|③|④|⑤|⑥|⑦)(：))|(【灵摆效果】)|(●)", desc)] + [len(desc)]
    parts_int: list[list[int]] = []  # [[0, 101], [101, 200], [200, 300], ...]
    options_int: list[list[int]] = []  # 带有●的列表，规范中要求后置

    for i in range(len(starts) - 1):
        next_index = i + 1
        if desc[starts[i]] != '●':  # 检查有无列表式选项
            while next_index < len(starts) - 1 and desc[starts[next_index]] == '●':
                next_index += 1  # 将文本涵盖这个选项

        start_pos = starts[i]
        end_pos = starts[next_index]
        if desc[end_pos - 1] == '\n':  # 不包含换行符
            end_pos -= 1

        if desc[start_pos] == '●':
            options_int.append([start_pos, end_pos])
        else:
            parts_int.append([start_pos, end_pos])

    parts_int += options_int  # 加入后置元素

    parts_int = list(filter(lambda x: desc[x[0]] != "【", parts_int))  # 【灵摆效果】本质上是没用的
    parts: list[list[int]] = [
        [len(desc[:start].encode("UTF-8")), len(desc[:end].encode("UTF-8"))]
        for start, end in parts_int
    ]
    if n_part != -1 and n_part != len(parts):
        # 如果分段数不对，就让每个段都是从头到尾的一样长度
        parts = [[0, len(desc.encode("UTF-8"))] for _ in range(n_part)]
        assert len(parts) == n_part
    return {
        "n_part": len(parts),
        "parts": flatten(parts),
        "segments": [desc[start:end] for start, end in parts_int],
    }


if __name__ == "__main__":
    split(r"")


def gen_part(
    card_data: CardData, card_raw_data: CardRawData, m_iCryptoKey: int
) -> bytes:
    """
    根据pidx生成part
    """
    # card_part 的十进制list(原版)
    card_part_full: list[int] = [int(x) for x in card_data["zh-cn"]["CARD_PART"]]
    # card_part 之中的变量二合一，然后删掉了前两个0
    card_part = [
        card_part_full[i] + card_part_full[i + 1] * 256
        for i, _ in enumerate(card_part_full)
        if i % 2 == 0
    ][2:]
    # card_pidx 的十进制list
    card_pidx_full: list[int] = [int(x) for x in card_data["zh-cn"]["CARD_PIDX"]]
    # card_pidx 二元组的第一个元素
    card_pidx_prefix: list[int] = [
        card_pidx_full[i] + card_pidx_full[i + 1] * 256
        for i, _ in enumerate(card_pidx_full)
        if i % 4 == 0
    ][1:]
    # card_pidx 二元组的第二个元素
    card_pidx_postfix: list[int] = [
        card_pidx_full[i] // 16 for i, _ in enumerate(card_pidx_full) if i % 4 == 3
    ][1:]

    # 下面验证发现的规律

    # * 第一：pidx的二元组的数量等于游戏中卡片数量，也就是说每个二元组对应一张卡
    assert len(card_pidx_prefix) == len(card_raw_data)

    # * 第三：pidx的二元组的前一位和下一个非空二元组的前一位的差值，就是当前二元组的后一位的值
    # * 修正：灵摆卡的pidx的后一位是1，前一位的结果才是真正的分段数
    # 所以，需要用二元组的前一位和后一位来合成真正的分段数
    card_pidx: list[int] = [0]
    last_idx: int = 0
    for i, e in enumerate(card_pidx_prefix):
        if e:
            card_pidx[last_idx] = e - card_pidx[last_idx]
            card_pidx.append(e)
            last_idx = i + 1
        else:
            card_pidx.append(0)
    last_desc = card_raw_data[last_idx - 1]["desc"]["zh-cn"]
    # 最后一张是灵摆卡的话 只能手动修正
    # 中文有可能掺杂英文 真让人迷惑...
    if last_desc.find("【灵摆效果】") != -1 and last_desc.find("[Pendulum Effect]") != -1:
        card_pidx[last_idx] = card_pidx_postfix[last_idx - 1]
    else:
        card_pidx[last_idx] = split(last_desc)["n_part"]
    del last_idx, last_desc
    card_pidx = card_pidx[1:]

    # for i in range(len(card_pidx)):
    #     if card_pidx[i] != card_pidx_postfix[i]:
    #         assert "灵摆效果" in card_raw_data[i]["desc"]["zh-cn"]

    # 接下来根据card_pidx来将card_part分段，里面每一项是一张卡的part
    part_each_card: list[list[int]] = []
    start = 0
    for n_part in card_pidx:
        part_each_card.append(card_part[start : start + n_part * 2])
        start += n_part * 2
    # 验证这种分段确实是正确的
    assert any([(part[0] < part[-1]) for part in part_each_card if part])

    card_segs: list[CardSegment] = []
    # 接下来对每张卡的desc custom计算新的分段，也就是说CardSegment
    for i, item in enumerate(card_raw_data):
        if not card_pidx[i]:
            continue
        desc_zh_cn = item["desc"]["zh-cn"]
        desc_custom = item["desc"]["custom"]
        seg: CardSegment = {
            "n_part": card_pidx[i],
            "is_pendulum": card_pidx_postfix[i] != card_pidx[i],  # 后期应该改成判断【灵摆效果】
            "parts_zh_cn": part_each_card[i],
            "segments_zh_cn": [],
            "parts_custom": [],
            "segments_custom": [],
        }

        # 验证
        # [[1, 10], [10, 20], ...]
        tmp: list[list[int]] = [
            [part_each_card[i][j], part_each_card[i][j + 1]]
            for j, _ in enumerate(part_each_card[i])
            if j % 2 == 0
        ]
        seg["segments_zh_cn"] = [
            desc_zh_cn.encode("UTF-8")[start:end].decode("UTF-8") for start, end in tmp
        ]
        split_result = split(desc_custom, seg["n_part"])

        seg["parts_custom"] = split_result["parts"]
        seg["segments_custom"] = split_result["segments"]

        # if item['name']['custom'] in ("增殖的G", '灰流丽', 'Y-龙头'):
        #     print(seg)
        card_segs.append(seg)

    # 合成新的card_part_full即可: 先加上俩0，然后一变二
    card_part_full_new: list[int] = flatten(
        [
            [y % 256, y // 256]
            for y in [0, 0, *flatten([x["parts_custom"] for x in card_segs])]
        ]
    )
    # 最后是加密
    return encrypt(m_iCryptoKey, bytes(card_part_full_new))
    # return encrypt(m_iCryptoKey, card_data["zh-cn"]["CARD_PART"])


T = TypeVar("T")


def encrypt(m_iCryptoKey: int, b: bytes) -> bytes:
    data = bytearray(zlib.compress(b))
    for i in range(len(data)):
        v = i + m_iCryptoKey + 0x23D
        v *= m_iCryptoKey
        v ^= i % 7
        data[i] ^= v & 0xFF
    return data


def card_encrypt(
    card_data: CardData,
    card_raw_data: CardRawData,
    m_iCryptoKey: int,
    custom_trans: bool = False,
) -> CardEncryptedData:
    def e(b: bytes) -> bytes:
        return encrypt(m_iCryptoKey, b)

    result: CardEncryptedData = cast(CardEncryptedData, {})
    result["CARD_PART"] = (
        gen_part(card_data, card_raw_data, m_iCryptoKey)
        if custom_trans
        else e(card_data["zh-cn"]["CARD_PART"])
    )
    result["CARD_PIDX"] = e(card_data["zh-cn"]["CARD_PIDX"])
    others = gen_others(card_raw_data, m_iCryptoKey)
    result["CARD_NAME"] = (
        others["CARD_NAME"] if custom_trans else e(card_data["zh-cn"]["CARD_NAME"])
    )
    result["CARD_DESC"] = (
        others["CARD_DESC"] if custom_trans else e(card_data["zh-cn"]["CARD_DESC"])
    )
    result["CARD_INDX"] = (
        others["CARD_INDX"] if custom_trans else e(card_data["zh-cn"]["CARD_INDX"])
    )

    return result
