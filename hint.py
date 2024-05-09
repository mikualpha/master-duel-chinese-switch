from typing import TypedDict, Literal

FileName = Literal["CARD_INDX", "CARD_NAME", "CARD_DESC", "CARD_PART", "CARD_PIDX", "CARD_PROP"]


CardData = TypedDict(
    "CardData", {"zh-cn": dict[FileName, bytes], "ja-jp": dict[FileName, bytes]}
)


CardRawDataName = TypedDict(
    "CardRawDataName", {"ja-jp": str, "zh-cn": str, "custom": str}
)
CardRawDataDesc = TypedDict("CardRawDataName", {"zh-cn": str, "custom": str})

CardRawDataItem = TypedDict(
    "CardRawDataItem", {"cid": int, "name": CardRawDataName, "desc": CardRawDataDesc}
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
    get_path_info: str = "拉取元数据..."
    searching_file: str = "扫描文件中(需较长时间)..."
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
    error_io: str = "无权限"
