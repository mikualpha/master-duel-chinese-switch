import zlib


def crack_key(b: bytes) -> int:
    def helper(b: bytes, m_iCryptoKey):
        data = bytearray(b)
        for i in range(len(data)):
            v = i + m_iCryptoKey + 0x23D
            v *= m_iCryptoKey
            v ^= i % 7
            data[i] ^= v & 0xFF
        zlib.decompress(data)

    for i in range(0xFF):
        m_iCryptoKey = i
        try:
            helper(b, m_iCryptoKey)
            return m_iCryptoKey
        except Exception as e:
            pass

    return -1
