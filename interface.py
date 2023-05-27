from ctypes import alignment
import webbrowser
from os import path
from typing import Any

import flet as ft

from index import main as install_trans
from utils import get_logger, throttle

RELEASE_URL = "https://github.com/mikualpha/master-duel-chinese-switch"

def log(e: Any) -> None:
    get_logger().error(e, stack_info=True)


def main(page: ft.Page):
    # 设置页面基础信息
    page.title = "No.86 卡片翻译切换"
    # page.bgcolor = "#f0f0f0"
    page.window_resizable = False
    page.window_height = 350
    page.window_width = 350
    page.padding = 0
    page.theme = ft.Theme(font_family="Microsoft YaHei")
    page.window_title_bar_buttons_hidden = True
    page.window_title_bar_hidden = True
    page.dark_theme = ft.Theme(font_family="Microsoft YaHei")
    page.theme_mode = ft.ThemeMode.DARK
    page.update()

    """
    设置标题栏
    """
    page.add(
        ft.Row(
            [
                ft.WindowDragArea(
                    ft.Container(
                        ft.Text(""), opacity=0, expand=True
                    ),
                    expand=True,
                ),
                ft.IconButton(
                    ft.icons.CLOSE,
                    icon_color="gray",
                    icon_size=15,
                    on_click=lambda _: page.window_destroy(),
                ),
            ]
        )
    )

    """
    dialog
    """

    def showDialog(content: str):
        def close_dlg(_):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            content=ft.Text(content),
            actions=[ft.TextButton("好的", on_click=close_dlg)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    """
    选择文件
    """

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            if e.files[0].name == "masterduel.exe":
                set_path_game_root(path.dirname(e.files[0].path))
                showDialog("选择成功")
            else:
                showDialog("选择失败，请选择游戏目录下的masterduel.exe文件")

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    btn_style = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))

    path_game_root: str = ""
    
    btn_select_game_root = ft.Ref[ft.ElevatedButton]()

    def set_path_game_root(p: str) -> None:
        nonlocal path_game_root
        path_game_root = p
        page.client_storage.set("path_game_root", p)
        if btn_select_game_root.current: # 按钮图标变化
            btn_select_game_root.current.icon = ft.icons.CHECK
    
    if p := page.client_storage.get("path_game_root"):
        set_path_game_root(p)

    """
    选择文件前的模态框
    """

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    def dlg_yes_callback(_):
        pick_files_dialog.pick_files(
            dialog_title="请选择游戏目录下的masterduel.exe文件", allowed_extensions=["exe"]
        )
        dlg_modal.open = False
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("重要提示"),
        content=ft.Text("请选择游戏目录下的masterduel.exe文件。\n不明白如何打开游戏目录请百度一下。"),
        actions=[
            ft.TextButton("取消", on_click=close_dlg),
            ft.TextButton("好的", on_click=dlg_yes_callback),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    """
    选项：翻译类型和字体
    """
    use_custom_trans: bool = True
    use_custom_font: bool = False
    output_to_local: bool = False

    def on_click_c1(e: ft.FilePickerResultEvent):
        nonlocal use_custom_trans
        use_custom_trans = e.data == "true"
        c1.label = "使用汉化组卡片翻译" if use_custom_trans else "使用官方简中卡片翻译"
        c1.update()

    def on_click_c2(e: ft.FilePickerResultEvent):
        nonlocal use_custom_font
        use_custom_font = e.data == "true"
        c2.label = "使用隶书卡片字体（目前有BUG请使用楷书）" if use_custom_font else "使用楷书卡片字体"
        c2.update()
    
    def on_click_c3(e: ft.FilePickerResultEvent):
        nonlocal output_to_local
        output_to_local = e.data == "true"
        c3.label = "输出到本地目录，便于手动覆盖" if output_to_local else "不输出到本地目录"
        c3.update()

    c1 = ft.Checkbox(label="使用汉化组卡片翻译", value=True, on_change=on_click_c1)
    c2 = ft.Checkbox(label="使用楷书卡片字体", value=False, on_change=on_click_c2)
    c3 = ft.Checkbox(label="不输出到本地目录", value=False, on_change=on_click_c3)

    """
    安装翻译
    """
    is_installing = False

    def install(_):
        nonlocal is_installing
        if is_installing:
            showDialog("正在安装中，请稍后")
            return
        if not path_game_root:
            showDialog("请选择游戏目录")
            return
        status_text.current.visible = True
        page.update()

        install_trans(
            path_game_root,
            set_status=status_update_cb,
            set_status_msg=status_update_msg_cb,
            network_error_cb=network_error_cb,
            log=log,
            custom_trans=use_custom_trans,
            custom_font=use_custom_font,
            output_to_local=output_to_local,
            dev_mode=False,
        )
        is_installing = False

    def status_update_cb(status: str):
        status_text.current.value = status
        status_text.current.update()
    
    def status_update_msg_cb(msg: str):
        status_text_msg.current.message = msg
        status_text_msg.current.visible = bool(msg)
        status_text_msg.current.update()
    
    @throttle(2)
    def network_error_cb():
        page.snack_bar = ft.SnackBar(ft.Text(f"网络错误，部分卡片将采用官方简中翻译。"))
        page.snack_bar.open = True
        page.update()

    status_text = ft.Ref[ft.Text]()
    status_text_msg = ft.Ref[ft.Tooltip]()

    # 添加到页面
    page.add(
        ft.Container(
            ft.Column(
                [
                    ft.Tooltip(
                        message="打开软件发布页",
                        content=ft.IconButton(
                            icon=ft.icons.JOIN_RIGHT_SHARP,
                            # icon=ft.icons.AUTO_MODE,
                            icon_size=50,
                            icon_color=ft.colors.BLUE_400,
                            on_click=lambda _: webbrowser.open(RELEASE_URL, 1),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.ElevatedButton(
                                "选择游戏目录",
                                ref=btn_select_game_root,
                                icon=ft.icons.ADD if not path_game_root else ft.icons.CHECK,
                                style=btn_style,
                                on_click=open_dlg_modal,
                            ),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        text="安装翻译",
                                        icon=ft.icons.CHEVRON_RIGHT,
                                        style=btn_style,
                                        on_click=install,
                                    ),
                                    ft.Tooltip(
                                        message="安装中",
                                        ref=status_text_msg,
                                        content=ft.Text(
                                            "安装中",
                                            ref=status_text,
                                            size=12,
                                            opacity=0.65,
                                            visible=False,
                                        )
                                    ), 
                                ],
                                spacing=15,
                            ),
                        ],
                        scale=ft.Scale(0.95, alignment=ft.alignment.top_left)
                    ),
                    ft.Column([c1, c2, c3], spacing=0, scale=ft.Scale(0.85, alignment=ft.alignment.top_left)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(-15, 50),
        )
    )


ft.app(target=main)
