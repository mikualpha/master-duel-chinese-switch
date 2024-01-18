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
from search import search_card_obj_list


# PATH: a04980f81c0a51d5
file_list = {  # Generate from search.py
    'CN': {'CARD_Prop': '5f538a2b', 'Card_Part': '885561fb', 'CARD_Indx': '8a5199d3', 'Card_Pidx': '9368c9bf', 'CARD_Name': 'ae1e31c7', 'CARD_Desc': 'fb88e395'}
}


def main(
    path_game_root: str,
    set_status: Callable[[str], None] = lambda _: print(_),
    set_status_msg: Callable[[str], None] = lambda _: print(_),
    log: Callable[[str], None] = lambda _: print(_),
    network_error_cb: Callable[[], None] = lambda: None,
    custom_trans: bool = True,
    custom_font: bool = False,
    output_to_local: bool = False,
    fix_missing_glyph: bool = False,
    search_card_obj: bool = False,
    dev_mode: bool = False,
):
    try:
        if search_card_obj:  # 是否需要搜索文件
            set_status(Status.searching_file)
            file_list['CN'] = search_card_obj_list(path_game_root, log)

        make_dir(get_resource_path("output"))
        set_status_msg("安装中...")

        # 首先 copy到本地
        set_status(Status.obtaining)
        path_data_unity3d = copy_to_local(path_game_root,
                                          get_resource_path("src"),
                                          file_list['CN'],
                                          dev_mode=dev_mode)

        set_status(Status.unpacking)
        card_data = card_unpack(path_data_unity3d)

        set_status(Status.cracking)
        m_iCryptoKey = crack_key(card_data["zh-cn"]["CARD_NAME"])
        # m_iCryptoKey = 95  # 现在为了减少时间先写死...
        # print("m_iCryptoKey =", m_iCryptoKey)

        set_status(Status.decrypting)
        card_data = card_decrypt(card_data, m_iCryptoKey)

        # for filename, data in card_data['zh-cn'].items():
        #     with open('./resources/' + filename + '.bin', 'wb') as f:
        #         f.write(data)

        set_status(Status.processing)
        card_raw_data = card_process(card_data)
        # print('CardRawData:', card_raw_data)

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
            card_encrypt_data, get_resource_path("src"), get_resource_path("output"), file_list['CN']
        )

        # 复制回去
        set_status(Status.overriding)  
        copy_to_original(
            path_game_root,
            path_pack=get_resource_path("output"),
            dir_font=get_resource_path("resources"),
            file_list=file_list['CN'],
            custom_font=custom_font,
            custom_trans=custom_trans,
            output_to_local=output_to_local,
            fix_missing_glyph=fix_missing_glyph,
            dev_mode=dev_mode
        )

        set_status(Status.success)
        set_status_msg("翻译成功！")

    except IOError as e:
        # 这儿对应无权限
        print(e)
        log(str(e))
        set_status(Status.error_io)
        set_status_msg('请以管理员身份运行本程序，\n或者勾选下面的"输出到本地目录"。')

    except Exception as e:
        # raise e
        print(e)
        log(str(e))
        set_status(Status.failed)


if __name__ == "__main__":
    # 测试
    main(
        r"F:\SteamLibrary\steamapps\common\Yu-Gi-Oh!  Master Duel",
        custom_trans=True,
        custom_font=False,
        output_to_local=True,  # 是否仅输出到本地
        dev_mode=True,
        search_card_obj=True,
    )
