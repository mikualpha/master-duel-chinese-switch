import json
from typing import Callable
from os import path

from crack_key import crack_key
from decrypt import card_decrypt
from encrypt import card_encrypt
from hint import CardRawData, Status
from move import copy_to_local, copy_to_original
from pack import card_pack
from process import card_process
from translate import card_translate
from unpack import card_unpack
from utils import make_dir, get_resource_path


def main(
    path_game_root: str,
    set_status: Callable[[str], None] = lambda _: print(_),
    log: Callable[[str], None] = lambda _: print(_),
    network_error_cb: Callable[[], None] = lambda: None,
    custom_trans: bool = True,
    custom_font: bool = False,
    dev_mode: bool = True,
):
    try:
        make_dir(get_resource_path("output"))

        # 首先 copy到本地
        set_status(Status.obtaining)
        path_data_unity3d = copy_to_local(path_game_root, get_resource_path("."))

        set_status(Status.unpacking)
        card_data = card_unpack(path_data_unity3d)

        set_status(Status.cracking)

        m_iCryptoKey = crack_key(card_data["ja-jp"]["CARD_NAME"])
        # m_iCryptoKey = 63  # 现在为了减少时间先写死...

        set_status(Status.decrypting)
        card_data = card_decrypt(card_data, m_iCryptoKey)

        set_status(Status.processing)
        card_raw_data = card_process(card_data)

        with open(
            path.join(get_resource_path("resources"), "card.json"), "r", encoding="utf8"
        ) as f:
            archived_Data: CardRawData = json.load(f)

        if custom_trans:
            set_status(Status.translating)
            # 恢复则无需翻译
            card_raw_data = card_translate(
                archived_Data,
                card_raw_data,
                progress_update_cb=(lambda _: None)
                if dev_mode
                else (lambda p: set_status(f"{Status.translating}: {p}")),
                network_error_cb=network_error_cb,
                dev_mode=dev_mode,
            )

        set_status(Status.encrypting)
        card_encrypt_data = card_encrypt(
            card_data, card_raw_data, m_iCryptoKey, custom_trans=custom_trans
        )

        set_status(Status.packing)
        card_pack(
            card_encrypt_data, get_resource_path("input"), get_resource_path("output")
        )

        # 复制回去
        set_status(Status.overriding)
        copy_to_original(
            path_game_root,
            path_output=get_resource_path("output"),
            dir_font=get_resource_path("resources"),
            custom_font=custom_font,
        )

        set_status(Status.success)

    except Exception as e:
        print(e)
        log(str(e))
        set_status(Status.failed)


if __name__ == "__main__":
    # 测试
    main(
        r"E:\Program Files (x86)\Steam\steamapps\common\Yu-Gi-Oh!  Master Duel",
        custom_trans=False,
        custom_font=False,
    )
