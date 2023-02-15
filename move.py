import shutil
from os import path
import os


def copy_to_local(path_game_root: str, path_resources: str) -> str:
    path_game_data_unity3d = path.join(
        path_game_root, "masterduel_Data", "data.unity3d"
    )
    path_local_data_unity3d = path.join(path_resources, "data.unity3d")
    shutil.copyfile(path_game_data_unity3d, path_local_data_unity3d)
    return path_local_data_unity3d


def copy_to_original(
    path_game_root: str, path_output: str, dir_font: str, custom_font: bool = False
) -> None:
    """
    复制path_output下的所有文件和文件夹到path_dst，若存在则覆盖
    """
    path_local_data = path.join(path_game_root, "LocalData")
    dirs = os.listdir(path_local_data)
    for dir in dirs:
        path_dst = path.join(path_local_data, dir, "0000")
        shutil.copytree(path_output, path_dst, dirs_exist_ok=True)
    copy_font(path_game_root, dir_font, custom_font=custom_font)


def copy_font(path_game_root: str, dir_font: str, custom_font: bool = False):
    FONT_FILE_NAME = "f36fce47"
    path_local_data = path.join(path_game_root, "LocalData")
    dirs = os.listdir(path_local_data)
    for dir in dirs:
        path_dst = path.join(path_local_data, dir, "0000", "f3", FONT_FILE_NAME)
        shutil.copyfile(
            path.join(
                dir_font,
                f"{FONT_FILE_NAME}_custom"
                if custom_font
                else f"{FONT_FILE_NAME}_zh_cn",
            ),
            path_dst,
        )
