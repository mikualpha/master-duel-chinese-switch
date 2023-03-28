import os
import shutil
from os import path

from utils import make_dir


def copy_to_local(path_game_root: str, path_resources: str) -> str:
    path_game_data_unity3d = path.join(
        path_game_root, "masterduel_Data", "data.unity3d"
    )
    path_local_data_unity3d = path.join(path_resources, "data.unity3d")
    shutil.copyfile(path_game_data_unity3d, path_local_data_unity3d)
    return path_local_data_unity3d


def copy_to_original(
    path_game_root: str,
    path_pack: str,
    dir_font: str,
    custom_font: bool = False,
    output_to_local: bool = False,
) -> None:
    """
    复制path_pack下的所有文件和文件夹到path_dst，若存在则覆盖
    """
    if output_to_local:
        # 本地输出
        make_dir(path.join(".", "output"))
        shutil.copytree(path_pack, path.join(".", "output"), dirs_exist_ok=True)
        for index, font in enumerate(fonts):
            path_font_dst = path.join(".", "output", font[:2])
            make_dir(path_font_dst)
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
        dirs = os.listdir(path_local_data)
        for dir in dirs:
            path_dst = path.join(path_local_data, dir, "0000")
            shutil.copytree(path_pack, path_dst, dirs_exist_ok=True)
        copy_font(path_game_root, dir_font, custom_font=custom_font)


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
