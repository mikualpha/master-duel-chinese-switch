import os
import shutil
from os import path

from utils import make_dir

BACKUP_FOLDER_NAME = "_TranslationBackup"


def get_local_data_key(path_game_root: str, file_list: dict[str, str]):
    path_local_data = path.join(path_game_root, "LocalData")
    dirs = os.listdir(path_local_data)

    key_list = []
    for x in dirs:
        ok = True
        for file_name in file_list.values():
            path_dst = path.join(path_local_data, x, "0000", file_name[:2], file_name)
            if not os.path.exists(path_dst):
                ok = False
                break

        if ok:
            key_list.append(x)
    return key_list


def createFolder(path: str):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)


def copy_to_local(path_game_root: str, path_resources: str, file_list: dict[str, str],
                  dev_mode: bool = False) -> dict[str, str]:
    local_file_name_list = {}
    data_keys = get_local_data_key(path_game_root, file_list)
    for data_key in data_keys:
        for file_type, file_name in file_list.items():
            if len(file_name) < 2:
                continue
            prefix = file_name[:2]

            game_data_path = path.join(path_game_root, "LocalData", data_key, "0000", prefix, file_name)
            local_data_dir = path.join(path_resources, prefix)
            local_data_path = path.join(path_resources, prefix, file_name)
            createFolder(local_data_dir)

            if not dev_mode:  # 非开发环境下进行备份
                recovery_dir = path.join(".", BACKUP_FOLDER_NAME, data_key, "0000", prefix)
                recovery_path = path.join(".", BACKUP_FOLDER_NAME, data_key, "0000", prefix, file_name)
                createFolder(recovery_dir)

                if not os.path.exists(recovery_path):  # 备份一份
                    shutil.copyfile(game_data_path, recovery_path)

            if not dev_mode or not os.path.exists(local_data_path):
                shutil.copyfile(game_data_path, local_data_path)

            local_file_name_list.setdefault(data_key, {})
            local_file_name_list[data_key][file_type] = local_data_path

    # 找一个数据最全的文件夹当输入
    input_key = None
    for k, v in local_file_name_list.items():
        if input_key is None:
            input_key = k
            continue

        if len(v) > len(local_file_name_list[k]):
            input_key = k
    return local_file_name_list[input_key]


def copy_to_original(
    path_game_root: str,
    path_pack: str,
    dir_font: str,
    file_list: dict[str, str],
    custom_font: bool = False,
    custom_trans: bool = True,
    output_to_local: bool = False,
    dev_mode: bool = False,
) -> None:
    """
    复制path_pack下的所有文件和文件夹到path_dst，若存在则覆盖
    """
    data_keys = get_local_data_key(path_game_root, file_list)
    for data_key in data_keys:
        if output_to_local:
            make_dir(path.join(".", "output"))
            shutil.copytree(path_pack, path.join(".", "output"), dirs_exist_ok=True)

            if custom_font:  # 这里先拦一下
                copy_font_to_local(path_game_root, data_key, dir_font, custom_font=custom_font, dev_mode=dev_mode)
        else:
            # 输出到游戏目录
            path_local_data = path.join(path_game_root, "LocalData")
            path_dst = path.join(path_local_data, data_key, "0000")

            if custom_trans:
                # 输出翻译
                shutil.copytree(path_pack, path_dst, dirs_exist_ok=True)

                # 输出字体
                copy_font(path_game_root, data_key, dir_font, custom_font=custom_font, dev_mode=dev_mode)
            elif not dev_mode:
                recovery_dir = path.join(".", BACKUP_FOLDER_NAME, data_key, "0000")
                shutil.copytree(recovery_dir, path_dst, dirs_exist_ok=True)


FONT_CARD_FILE_NAME_CN = "f36fce47"     # FZBWKSJW
SDF_CARD_FILE_NAME_CN = "7a7d18a0"      # FZBWKSJW - Font SDF Atlas
FONT_CARD_FILE_NAME_EN = "ce4734d3"
FONT_CARD_FILE_NAME_JP = "c09bd125"
FONT_UI_509R_FILE_NAME_CN = "25946b17"  # FZYouHJW_509R
FONT_UI_512R_FILE_NAME_CN = "da15c88f"  # FZYouHJW_512R

# 字体文件列表
fonts = (FONT_CARD_FILE_NAME_CN, SDF_CARD_FILE_NAME_CN, FONT_UI_509R_FILE_NAME_CN, FONT_UI_512R_FILE_NAME_CN,
         FONT_CARD_FILE_NAME_EN,
         FONT_CARD_FILE_NAME_JP)
# 有Custom版本的文件列表
custom_fonts = (FONT_CARD_FILE_NAME_CN, SDF_CARD_FILE_NAME_CN,
                FONT_UI_509R_FILE_NAME_CN, FONT_UI_512R_FILE_NAME_CN)


def copy_font_to_local(path_game_root: str, data_key: str, dir_font: str, custom_font: bool = False,
                       dev_mode: bool = False):
    for index, font in enumerate(fonts):
        dst_path = path.join(path_game_root, "LocalData", data_key, "0000", font[:2], font)
        # if not os.path.exists(dst_path):  # 目标文件不存在(说明可能是无效的data_key)
        #     return

        path_font_dst = path.join(".", "output", font[:2])
        make_dir(path_font_dst)

        if not dev_mode:  # 非开发环境下进行备份
            createFolder(path.join(".", BACKUP_FOLDER_NAME, data_key, "0000", font[:2]))
            shutil.copyfile(  # 备份
                dst_path,
                path.join(".", BACKUP_FOLDER_NAME, data_key, "0000", font[:2], font)
            )

        # 输出到output
        if font in custom_fonts:
            src_filename = f"{font}_custom" if custom_font else f"{font}_zh_cn"
        else:
            src_filename = font
        shutil.copyfile(
            path.join(dir_font, src_filename),
            path.join(path_font_dst, font),
        )


def copy_font(path_game_root: str, data_key: str, dir_font: str, custom_font: bool = False, dev_mode: bool = False):
    path_local_data = path.join(path_game_root, "LocalData")
    for index, font in enumerate(fonts):
        dst_path = path.join(path_local_data, data_key, "0000", font[:2], font)
        # if not os.path.exists(dst_path):  # 目标文件不存在(说明可能是无效的data_key)
        #     return

        if not dev_mode:  # 非开发环境下进行备份
            createFolder(path.join(".", BACKUP_FOLDER_NAME, data_key, "0000", font[:2]))
            shutil.copyfile(  # 备份
                dst_path,
                path.join(".", BACKUP_FOLDER_NAME, data_key, "0000", font[:2], font)
            )

        # 输出到游戏目录
        if font in custom_fonts:
            src_filename = f"{font}_custom" if custom_font else f"{font}_zh_cn"
        else:
            src_filename = font
        shutil.copyfile(
            path.join(dir_font, src_filename),
            dst_path
        )
