import os
import shutil
from os import path

from utils import make_dir

LOCAL_DATA_KEY = 'c7afc9a7'


def createFolder(path: str):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)


def copy_to_local(path_game_root: str, path_resources: str, file_list: dict[str, str],
                  dev_mode: bool = False) -> dict[str, str]:
    local_file_name_list = {}
    for file_name, file_path in file_list.items():
        if len(file_path) < 2:
            continue
        prefix = file_path[:2]
        game_data_path = path.join(path_game_root, "LocalData", LOCAL_DATA_KEY, "0000", prefix, file_path)
        local_data_dir = path.join(path_resources, prefix)
        local_data_path = path.join(path_resources, prefix, file_path)
        recovery_dir = path.join(".", "_TranslationBackup", LOCAL_DATA_KEY, "0000", prefix)
        recovery_path = path.join(".", "_TranslationBackup", LOCAL_DATA_KEY, "0000", prefix, file_path)
        createFolder(local_data_dir)
        createFolder(recovery_dir)

        if not dev_mode or not os.path.exists(local_data_path):
            shutil.copyfile(game_data_path, local_data_path)

        if not os.path.exists(recovery_path):  # 备份一份
            shutil.copyfile(game_data_path, recovery_path)

        local_file_name_list[file_name] = local_data_path
    return local_file_name_list


def copy_to_original(
    path_game_root: str,
    path_pack: str,
    dir_font: str,
    custom_font: bool = False,
    custom_trans: bool = True,
    output_to_local: bool = False,
) -> None:
    """
    复制path_pack下的所有文件和文件夹到path_dst，若存在则覆盖
    """
    if output_to_local:
        make_dir(path.join(".", "output"))
        shutil.copytree(path_pack, path.join(".", "output"), dirs_exist_ok=True)

        if custom_font:
            for index, font in enumerate(fonts):
                path_font_dst = path.join(".", "output", font[:2])
                make_dir(path_font_dst)
                shutil.copyfile(  # 备份
                    path.join(path_font_dst, font),
                    path.join(".", "_TranslationBackup", LOCAL_DATA_KEY, "0000", font[:2], font)
                )
                shutil.copyfile(
                    path.join(
                        dir_font,
                        (f"{font}_custom"
                        if custom_font
                        else f"{font}_zh_cn")
                        if index == 0
                        else font,
                    ),
                    path.join(path_font_dst, font),
                )
    else:
        # 输出到游戏目录
        path_local_data = path.join(path_game_root, "LocalData")
        path_dst = path.join(path_local_data, LOCAL_DATA_KEY, "0000")
        if custom_trans:
            shutil.copytree(path_pack, path_dst, dirs_exist_ok=True)
            copy_font(path_game_root, dir_font, custom_font=custom_font)
        else:
            recovery_dir = path.join(".", "_TranslationBackup", LOCAL_DATA_KEY, "0000")
            shutil.copytree(recovery_dir, path_dst, dirs_exist_ok=True)


FONT_FILE_NAME = "f36fce47"
FONT_FILE_NAME_EN = "ce4734d3"
FONT_FILE_NAME_JP = "c09bd125"
fonts = [FONT_FILE_NAME, FONT_FILE_NAME_EN, FONT_FILE_NAME_JP]


def copy_font(path_game_root: str, dir_font: str, custom_font: bool = False):
    path_local_data = path.join(path_game_root, "LocalData")
    dirs = os.listdir(path_local_data)
    for index, font in enumerate(fonts):
        for dir in dirs:
            path_dst = path.join(path_local_data, dir, "0000", font[:2], font)
            shutil.copyfile(
                path.join(
                    dir_font,
                    (f"{font}_custom"
                    if custom_font
                    else f"{font}_zh_cn")
                    if index == 0
                    else font,
                ),
                path_dst,
            )
