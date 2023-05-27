from hint import CardData, CardRawData, CardRawDataItem


# Name Desc 的 start 分别是 0 4
def progressiveProcess(
    b: bytes, b_indx: bytes, start: int, should_skip: bool = True
) -> list[str]:

    # 读取二进制indx
    hex_str_list = ("{:02X}".format(int(c)) for c in b_indx)  # 定义变量接受文件内容
    dec_list = [int(s, 16) for s in hex_str_list]  # 将十六进制转换为十进制

    # 拿到desc的indx
    _indx: list[list[int]] = []
    for i in range(start, len(dec_list), 8 if should_skip else 4):
        tmp: list[int] = []
        for j in range(4):
            tmp.append(dec_list[i + j])
        _indx.append(tmp)

    def fourToOne(x: list[int]) -> int:
        res = 0
        for i in range(3, -1, -1):
            res *= 16 * 16
            res += x[i]
        return res

    indx = [fourToOne(i) for i in _indx]
    indx = indx[1:]
    """
    将解密后的CARD文件转换为JSON文件
    """

    def solve(data: bytes, desc_indx: list[int]) -> list[str]:
        res: list[str] = []
        for i in range(len(desc_indx) - 1):
            s = data[desc_indx[i] : desc_indx[i + 1]]
            s = s.decode("UTF-8")
            while len(s) > 0 and s[-1] == "\u0000":
                s = s[:-1]
            res.append(s)
        return res

    return solve(b, indx)


def card_process(card_data: CardData) -> CardRawData:
    # CARD_Name_jp = progressiveProcess(
    #     card_data["ja-jp"]["CARD_NAME"], card_data["ja-jp"]["CARD_INDX"], 0
    # )
    CARD_Name_zh = progressiveProcess(
        card_data["zh-cn"]["CARD_NAME"], card_data["zh-cn"]["CARD_INDX"], 0
    )
    CARD_Desc_zh = progressiveProcess(
        card_data["zh-cn"]["CARD_DESC"], card_data["zh-cn"]["CARD_INDX"], 4
    )
    res: CardRawData = []
    for i in range(len(CARD_Name_zh)):
        tmp: CardRawDataItem = {
            "indx": i,
            "name": {
                # "ja-jp": CARD_Name_jp[i],
                "ja-jp": "",
                "zh-cn": CARD_Name_zh[i],
                "custom": ""
            },
            "desc": {
                "zh-cn": CARD_Desc_zh[i],
                "custom": ""
            },
        }
        res.append(tmp)
    return res
