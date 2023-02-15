from typing import TypedDict, Literal

FileName = Literal["CARD_INDX", "CARD_NAME", "CARD_DESC", "CARD_PART", "CARD_PIDX"]


CardData = TypedDict(
    "CardData", {"zh-cn": dict[FileName, bytes], "ja-jp": dict[FileName, bytes]}
)


CardRawDataName = TypedDict(
    "CardRawDataName", {"ja-jp": str, "zh-cn": str, "custom": str}
)
CardRawDataDesc = TypedDict("CardRawDataName", {"zh-cn": str, "custom": str})

CardRawDataItem = TypedDict(
    "CardRawDataItem", {"indx": int, "name": CardRawDataName, "desc": CardRawDataDesc}
)

CardRawData = list[CardRawDataItem]

PathIdDict = TypedDict("PathIdDict", {"ja-jp": dict[int, str], "zh-cn": dict[int, str]})


class CardEncryptedData(TypedDict):
    CARD_INDX: bytes
    CARD_NAME: bytes
    CARD_DESC: bytes
    CARD_PART: bytes
    CARD_PIDX: bytes


class Status:
    obtaining: str = "提取中"
    unpacking: str = "解包中"
    cracking: str = "轮询密钥中"
    decrypting: str = "解密中"
    processing: str = "处理中"
    translating: str = "翻译中"
    encrypting: str = "加密中"
    packing: str = "打包中"
    overriding: str = "覆写中"
    success: str = "成功"
    failed: str = "失败"
    error_network: str = "网络错误"
