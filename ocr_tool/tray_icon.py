"""
系统托盘图标模块
"""

import threading
import pystray
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Callable
from config import load_config


class TrayIcon:
    """系统托盘管理器"""

    def __init__(self):
        self.icon = None
        self.menu_callbacks = {}
        self._create_icon_image()
        self.config = load_config()

    def _create_icon_image(self, size: int = 64) -> Image.Image:
        """创建托盘图标（OCR文字A图标）

        Returns:
            PIL Image对象
        """
        # 创建图像（白色背景）
        image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # 绘制蓝色圆形背景
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(0, 120, 215, 255),  # Windows蓝色
            outline=(0, 90, 170, 255)
        )

        # 绘制"OCR"文字
        try:
            # 尝试使用默认字体
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = "OCR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 2
        draw.text((x, y), text, fill="white", font=font)

        self.icon_image = image
        return image

    def set_menu(self, actions: dict):
        """设置托盘菜单

        Args:
            actions: 菜单项字典 {名称: 回调函数}
        """
        self.menu_callbacks = actions

    def run(self):
        """运行托盘图标（在独立线程中）"""
        menu_items = []

        # 菜单项顺序
        menu_order = [
            ("截图OCR", self._on_screenshot),
            ("打开设置", self._on_settings),
            ("退出", self._on_exit)
        ]

        for label, callback in menu_order:
            if label in self.menu_callbacks:
                menu_items.append(pystray.MenuItem(label, callback))
            else:
                menu_items.append(pystray.MenuItem(label, callback))

        menu = pystray.Menu(*menu_items)

        self.icon = pystray.Icon(
            name="OCR Tool",
            icon=self.icon_image,
            title="OCR截图工具",
            menu=menu
        )

        # 运行托盘（阻塞）
        self.icon.run()

    def stop(self):
        """停止托盘"""
        if self.icon:
            self.icon.stop()

    def notify(self, title: str, message: str):
        """显示通知（气泡提示）

        Args:
            title: 标题
            message: 消息内容
        """
        if self.icon and self.config.get("show_notification", True):
            self.icon.notify(message, title)

    def _on_screenshot(self, icon, item):
        """菜单 - 截图"""
        if "screenshot" in self.menu_callbacks:
            self.menu_callbacks["screenshot"]()

    def _on_settings(self, icon, item):
        """菜单 - 设置"""
        if "settings" in self.menu_callbacks:
            self.menu_callbacks["settings"]()

    def _on_exit(self, icon, item):
        """菜单 - 退出"""
        self.stop()
        import os
        os._exit(0)  # 强制退出所有线程


def run_tray(actions: dict) -> TrayIcon:
    """启动系统托盘的便捷函数

    Args:
        actions: 菜单回调字典

    Returns:
        TrayIcon实例
    """
    tray = TrayIcon()
    tray.set_menu(actions)
    thread = threading.Thread(target=tray.run, daemon=True)
    thread.start()
    return tray
