import zlib
from typing import cast

from hint import CardData


def card_decrypt(unpacked: CardData, m_iCryptoKey: int) -> CardData:
    result: CardData = cast(CardData, {"zh-cn": {}, "ja-jp": {}})
    for lang in unpacked.keys():
        for name, b in unpacked[lang].items():
            data = bytearray(cast(bytes, b))

            for i in range(len(data)):
                v = i + m_iCryptoKey + 0x23D
                v *= m_iCryptoKey
                v ^= i % 7
                data[i] ^= v & 0xFF

            result[lang][name] = zlib.decompress(data)

    return result
