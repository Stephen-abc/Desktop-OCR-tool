#!/usr/bin/env python3
"""
OCR截图工具 - 主程序入口
"""

import sys
import os
import traceback
from typing import Optional

# 确保项目路径在sys.path中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入本地模块
from config import load_config
from ocr_engine import get_ocr_engine
from screenshot import ScreenshotSelector, grab_area
from clipboard import copy_text
from tray_icon import TrayIcon, run_tray
from hotkey import HotkeyManager
from settings_window import SettingsWindow


class OCRTool:
    """OCR工具主类"""

    def __init__(self):
        self.config = load_config()
        self.hotkey_manager = HotkeyManager()
        self.tray_icon: Optional[TrayIcon] = None
        self.settings_window: Optional[SettingsWindow] = None
        self.ocr_engine = None
        self._running = True

        print("=" * 50)
        print("本地OCR截图工具启动中...")
        print(f"热键: {self.config.get('hotkey')}")
        print(f"OCR语言: {self.config.get('ocr_lang')}")
        print("=" * 50)

    def _init_ocr(self):
        """初始化OCR引擎（延迟加载）"""
        try:
            lang = self.config.get('ocr_lang', 'ch')
            model_path = self.config.get('model_path')
            print("正在加载OCR引擎...")
            self.ocr_engine = get_ocr_engine(lang=lang, model_path=model_path)
            print("OCR引擎就绪")
            return True
        except Exception as e:
            print(f"OCR引擎初始化失败: {e}")
            print("首次运行可能需要下载模型文件，请稍后重试")
            return False

    def _do_ocr_screenshot(self):
        """执行截图并OCR"""
        try:
            # 1. 截图选择
            print("\n" + "=" * 50)
            print("开始截图 - 拖拽选择区域，右键确认，ESC取消")
            print("=" * 50)

            selector = ScreenshotSelector()
            area = selector.ask_screenshot()

            if not area:
                print("截图已取消")
                return

            print(f"选区: {area}")

            # 2. 截取图像
            img = grab_area(area)

            # 3. 识别文字
            print("正在识别文字...")
            if self.ocr_engine is None:
                if not self._init_ocr():
                    self._show_notification("OCR未就绪", "请检查安装或稍后重试")
                    return

            text = self.ocr_engine.recognize(img)

            if not text or not text.strip():
                self._show_notification("未识别到文字", "请选择包含文字的清晰图片")
                print("未识别到文字")
                return

            print(f"识别结果: {text[:100]}...")

            # 4. 复制到剪贴板
            success, msg = copy_text(text)
            if success:
                print(msg)
                self._show_notification("OCR完成", msg)
            else:
                self._show_notification("复制失败", msg)

        except Exception as e:
            error_msg = f"OCR过程出错: {e}"
            print(error_msg)
            traceback.print_exc()
            self._show_notification("错误", error_msg)

    def _show_notification(self, title: str, message: str):
        """显示托盘通知"""
        if self.tray_icon:
            self.tray_icon.notify(title, message)

    def _on_settings(self):
        """打开设置窗口"""
        if self.settings_window and self.settings_window.window:
            self.settings_window.window.lift()
            return

        def on_save():
            print("设置已更新")
            # 配置已由SettingsWindow保存，这里可以执行其他更新操作

        self.settings_window = SettingsWindow(
            hotkey_manager=self.hotkey_manager,
            on_save_callback=on_save
        )

        # 在新线程中运行Tkinter窗口，避免阻塞主线程
        import threading
        thread = threading.Thread(target=self.settings_window.show, daemon=True)
        thread.start()

    def _on_exit(self):
        """退出程序"""
        print("正在退出...")
        self._running = False
        self.hotkey_manager.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        os._exit(0)

    def run(self):
        """运行主程序"""
        try:
            # 设置热key回调
            self.hotkey_manager.set_callback(self._do_ocr_screenshot)

            # 启动热key监听
            self.hotkey_manager.start()

            # 启动托盘图标
            menu_actions = {
                'screenshot': self._do_ocr_screenshot,
                'settings': self._on_settings,
                'exit': self._on_exit
            }

            self.tray_icon = run_tray(menu_actions)

            print("程序已运行，在系统托盘中")
            print(f"按 {self.config.get('hotkey')} 或右键点击进行截图OCR")
            print("按 Ctrl+C 退出（如果看到控制台窗口）")

            # 保持主线程运行
            import time
            while self._running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n正在退出...")
            self._on_exit()
        except Exception as e:
            print(f"程序运行出错: {e}")
            traceback.print_exc()


def main():
    """主入口"""
    try:
        app = OCRTool()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")


if __name__ == "__main__":
    main()
