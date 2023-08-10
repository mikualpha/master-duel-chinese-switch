import os
import shutil
from os import path


class BackupFileManager(object):
    BACKUP_FOLDER_NAME = "_TranslationBackup"

    @staticmethod
    def backup_file(data_key, path_game_root, file_name, dev_mode):  # src_dir不用带LocalData
        """
        备份文件，当文件已存在时，不覆盖
        """
        if dev_mode:
            return
        if len(file_name) < 2:
            return
        prefix = file_name[:2]
        recovery_dir = path.join(".", BackupFileManager.BACKUP_FOLDER_NAME, data_key, "0000", prefix)
        recovery_path = path.join(".", BackupFileManager.BACKUP_FOLDER_NAME, data_key, "0000", prefix, file_name)

        if os.path.exists(recovery_path):  # 文件已存在就不备份了
            return

        create_folder(recovery_dir)
        src_path = path.join(path_game_root, "LocalData", data_key, "0000", prefix, file_name)
        shutil.copyfile(src_path, recovery_path)

    @staticmethod
    def recovery_file(data_key, dst_dir, file_name, dev_mode):
        """
        从备份恢复指定文件到指定目录
        """
        if dev_mode:
            return
        if len(file_name) < 2:
            return
        prefix = file_name[:2]

        dst_path = path.join(dst_dir, data_key, "0000", prefix, file_name)
        recovery_path = path.join(".", BackupFileManager.BACKUP_FOLDER_NAME, data_key, "0000", prefix, file_name)
        if not os.path.exists(recovery_path):  # 文件不存在
            return

        shutil.copyfile(recovery_path, dst_path)


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


def create_folder(folder_path: str):
    folder_path = folder_path.strip()
    folder_path = folder_path.rstrip("\\")
    is_exists = os.path.exists(folder_path)
    if not is_exists:
        os.makedirs(folder_path)


# 开始阶段 - 取文件到本地
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
            create_folder(local_data_dir)

            # 备份文件
            BackupFileManager.backup_file(data_key, path_game_root, file_name, dev_mode)

            local_file_name_list.setdefault(data_key, {})
            local_file_name_list[data_key][file_type] = local_data_path

            # 开发者模式只Copy一次
            if dev_mode and os.path.exists(local_data_path):
                continue

            shutil.copyfile(game_data_path, local_data_path)

    # 找一个数据最全的文件夹当输入
    input_key = None
    for k, v in local_file_name_list.items():
        if input_key is None:
            input_key = k
            continue

        if len(v) > len(local_file_name_list[k]):
            input_key = k
    return local_file_name_list[input_key]


# 结束阶段 - 把修改好的文件复制回去
def copy_to_original(
    path_game_root: str,
    path_pack: str,
    dir_font: str,
    file_list: dict[str, str],
    custom_font: bool = False,
    custom_trans: bool = True,
    output_to_local: bool = False,
    fix_missing_glyph: bool = False,
    dev_mode: bool = False,
) -> None:
    """
    复制path_pack下的所有文件和文件夹到path_dst，若存在则覆盖
    """
    if output_to_local:  # 输出到本地文件夹
        if dev_mode:  # 防止循环复制，拦截
            return
        create_folder(path.join(".", "output"))
        dst_dir = path.join(".", "output")
    else:
        dst_dir = path.join(path_game_root, "LocalData")

    data_keys = get_local_data_key(path_game_root, file_list)
    for data_key in data_keys:
        # 安装翻译
        path_dst = path.join(dst_dir, data_key, "0000")

        if custom_trans:  # 输出翻译
            shutil.copytree(path_pack, path_dst, dirs_exist_ok=True)
        else:  # 还原翻译
            for file_name in file_list.values():
                BackupFileManager.recovery_file(data_key, dst_dir, file_name, dev_mode)

        # 输出字体
        output_font(path_game_root, data_key, dst_dir, dir_font, list(normal_fonts),
                    custom_font=custom_font, dev_mode=dev_mode)

        # 修复字体
        output_font(path_game_root, data_key, dst_dir, dir_font, list(fix_fonts),
                    custom_font=fix_missing_glyph, dev_mode=dev_mode)


FONT_CARD_FILE_NAME_CN = "f36fce47"     # FZBWKSJW
SDF_CARD_FILE_NAME_CN = "7a7d18a0"      # FZBWKSJW - Font SDF Atlas
# FONT_CARD_FILE_NAME_EN = "ce4734d3"
# FONT_CARD_FILE_NAME_JP = "c09bd125"
FONT_UI_509R_FILE_NAME_CN = "25946b17"  # FZYouHJW_509R
FONT_UI_512R_FILE_NAME_CN = "da15c88f"  # FZYouHJW_512R

# 替换必需的字体文件列表
normal_fonts = (FONT_CARD_FILE_NAME_CN, SDF_CARD_FILE_NAME_CN)

# 修复缺字问题的字体文件列表
# 目前需要修复的字：魊
fix_fonts = (FONT_UI_509R_FILE_NAME_CN, FONT_UI_512R_FILE_NAME_CN)


def output_font(path_game_root: str, data_key: str, dst_dir: str, dir_font: str, fonts: list[str],
                custom_font: bool = False, dev_mode: bool = False):
    for index, font in enumerate(fonts):
        if custom_font:  # 替换字体
            BackupFileManager.backup_file(data_key, path_game_root, font, dev_mode)

            src_filename = f"{font}_custom"
            src_file_path = path.join(dir_font, src_filename)
            if not os.path.exists(src_file_path):  # 文件不存在？
                print("Error: 文件不存在: ", src_file_path)
                continue

            dst_file_dir = path.join(dst_dir, data_key, "0000", font[:2])
            dst_file_path = path.join(dst_file_dir, font)

            create_folder(dst_file_dir)
            shutil.copyfile(src_file_path, dst_file_path)
        else:  # 还原备份
            BackupFileManager.recovery_file(data_key, dst_dir, font, dev_mode)
