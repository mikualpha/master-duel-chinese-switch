import time
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
    page.window.resizable = False
    page.window.height = 410
    page.window.width = 360
    page.padding = 0
    page.theme = ft.Theme(font_family="Microsoft YaHei")
    page.window.title_bar_buttons_hidden = True
    page.window.title_bar_hidden = True
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
                    on_click=lambda _: page.window.close() and page.window.destroy(),
                ),
            ]
        )
    )

    """
    dialog
    """

    def showDialog(content: str | ft.Text, title_text: str = None, button_text: str = "好的"):
        def close_dlg(_):
            dlg.open = False
            page.update()

        if title_text:
            dlg = ft.AlertDialog(
                title=ft.Text(title_text),
                content=ft.Text(content) if type(content) is str else content,
                actions=[ft.TextButton(button_text, on_click=close_dlg)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        else:
            dlg = ft.AlertDialog(
                content=ft.Text(content) if type(content) is str else content,
                actions=[ft.TextButton(button_text, on_click=close_dlg)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        page.overlay.append(dlg)
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
        if btn_select_game_root.current:  # 按钮图标变化
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
        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        page.update()

    """
    选项：翻译类型和字体
    """
    use_custom_trans: bool = True
    use_custom_font: bool = True
    fix_missing_glyph: bool = True
    output_to_local: bool = False
    search_card_obj: bool = False

    def on_click_c1(e: ft.FilePickerResultEvent):
        nonlocal use_custom_trans
        use_custom_trans = e.data == "true"
        c1.label = "使用汉化组卡片翻译" if use_custom_trans else "使用官方简中卡片翻译"
        c1.update()

    def on_click_c2(e: ft.FilePickerResultEvent):
        nonlocal use_custom_font
        use_custom_font = e.data == "true"
        c2.label = "使用隶书卡片字体" if use_custom_font else "使用楷书卡片字体"
        c2.update()

    def on_click_c3(e: ft.FilePickerResultEvent):
        nonlocal fix_missing_glyph
        fix_missing_glyph = e.data == "true"
        c3.label = "修复部分生僻字缺字问题" if fix_missing_glyph else "不进行缺字问题修复"
        c3.update()

    def on_click_c4(e: ft.FilePickerResultEvent):
        nonlocal output_to_local
        output_to_local = e.data == "true"
        c4.label = "输出到本地目录，便于手动覆盖" if output_to_local else "不输出到本地目录"
        c4.update()

    def on_click_c5(e: ft.FilePickerResultEvent):
        nonlocal search_card_obj
        search_card_obj = e.data == "true"
        if search_card_obj:
            c5.label = "本项请仅在有开发者指引的情况下勾选！！"
            c5.fill_color = ft.colors.RED
        else:
            c5.label = "扫描游戏目录以查找文件(切勿随意勾选)"
            c5.fill_color = None
        c5.update()

    c1 = ft.Checkbox(label="使用汉化组卡片翻译", value=True, on_change=on_click_c1)
    c2 = ft.Checkbox(label="使用隶书卡片字体", value=True, on_change=on_click_c2)
    c3 = ft.Checkbox(label="修复部分生僻字缺字问题", value=True, on_change=on_click_c3)  # , disabled=True
    c4 = ft.Checkbox(label="不输出到本地目录", value=False, on_change=on_click_c4)
    c5 = ft.Checkbox(label="扫描游戏目录以查找文件(切勿随意勾选)", value=False, on_change=on_click_c5)

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
            network_error_cb=network_error_cb,
            log=log,
            custom_trans=use_custom_trans,
            custom_font=use_custom_font,
            output_to_local=output_to_local,
            fix_missing_glyph=fix_missing_glyph,
            search_card_obj=search_card_obj,
            dev_mode=False,
        )
        is_installing = False

    def status_update_cb(status: str):
        status_text.current.value = status
        status_text.current.update()

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
                    ft.IconButton(
                        icon=ft.icons.JOIN_RIGHT_SHARP,
                        # icon=ft.icons.AUTO_MODE,
                        icon_size=50,
                        icon_color=ft.colors.BLUE_400,
                        on_click=lambda _: webbrowser.open(RELEASE_URL, 1),
                        tooltip=ft.Tooltip(
                            message="打开软件发布页",
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
                                    ft.Text(
                                        "安装中",
                                        ref=status_text,
                                        size=12,
                                        opacity=0.65,
                                        visible=False,
                                    )

                                ],
                                spacing=15,
                            ),
                        ],
                        scale=ft.Scale(0.95, alignment=ft.alignment.top_left)
                    ),
                    ft.Column([c1, c2, c3, c4, c5], spacing=0, scale=ft.Scale(0.85, alignment=ft.alignment.top_left)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(-15, 50),
        )
    )

    if not page.client_storage.get("copyright_notice"):
        time.sleep(0.5)
        showDialog(ft.Text(
            disabled=False,
            # size=15,
            spans=[
                ft.TextSpan("    "),
                ft.TextSpan("本项目为开源项目，只会通过"),
                ft.TextSpan(
                    "GitHub页面",
                    ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE,
                                 decoration_color=ft.colors.BLUE,
                                 color=ft.colors.BLUE),
                    url=RELEASE_URL,
                ),
                ft.TextSpan("发布版本更新，不存在任何官方群，不会通过其它任何渠道发布，不存在任何购买、捐赠、打赏等付费入口，谨防木马病毒感染或上当受骗！"),
            ],
        ), title_text="声明", button_text="明白")
        page.client_storage.set("copyright_notice", 1)


ft.app(target=main)
