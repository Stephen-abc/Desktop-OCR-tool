"""
截图模块 - 区域选择和捕获
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple
import numpy as np
from PIL import ImageGrab, Image, ImageTk


class ScreenshotSelector:
    """截图区域选择器"""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selected_area = None  # (x1, y1, x2, y2)
        self.screen_width = 0
        self.screen_height = 0
        self._setup_screen_info()

    def _setup_screen_info(self) -> None:
        """获取屏幕尺寸"""
        # 使用PIL的ImageGrag获取所有屏幕
        try:
            # 获取主显示器尺寸
            from PIL import ImageGrab
            img = ImageGrab.grab()
            self.screen_width, self.screen_height = img.size
        except Exception as e:
            print(f"获取屏幕尺寸失败: {e}")
            # 回退到默认
            self.screen_width = 1920
            self.screen_height = 1080

    def ask_screenshot(self) -> Optional[Tuple[int, int, int, int]]:
        """显示截图选择界面，返回选区坐标 (x1, y1, x2, y2)"""
        self.selected_area = None

        # 创建全屏透明窗口
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 透明度30%
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        self.root.cursor = "cross"

        # 创建Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0
        )
        self.canvas.pack()

        # 绑定事件
        self.canvas.bind('<Button-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)
        self.root.bind('<Escape>', lambda e: self._cancel())
        self.root.bind('<Button-3>', lambda e: self._confirm())  # 右键确认

        # 提示文字
        self.canvas.create_text(
            self.screen_width // 2, 50,
            text="拖拽选择截图区域 | ESC取消 | 右键确认",
            fill="white", font=("Arial", 16)
        )

        # 启动主循环
        self.root.mainloop()

        return self.selected_area

    def _on_press(self, event):
        """鼠标按下"""
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = None

    def _on_drag(self, event):
        """鼠标拖拽"""
        if self.start_x is None or self.start_y is None:
            return

        cur_x, cur_y = event.x, event.y
        # 删除旧的矩形
        if self.rect:
            self.canvas.delete(self.rect)

        # 绘制新矩形
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline="red", width=2, fill='black', stipple="gray25"
        )

        # 显示尺寸
        size_text = f"{abs(cur_x - self.start_x)} x {abs(cur_y - self.start_y)}"
        self.canvas.delete("size_text")
        self.canvas.create_text(
            cur_x + 10, cur_y + 10,
            text=size_text, fill="yellow", font=("Arial", 12),
            tags="size_text"
        )

    def _on_release(self, event):
        """鼠标释放"""
        if self.start_x is None or self.start_y is None:
            return

        end_x, end_y = event.x, event.y
        self.selected_area = (
            min(self.start_x, end_x),
            min(self.start_y, end_y),
            max(self.start_x, end_x),
            max(self.start_y, end_y)
        )

        # 选区太小忽略
        width = self.selected_area[2] - self.selected_area[0]
        height = self.selected_area[3] - self.selected_area[1]
        if width < 5 or height < 5:
            self.selected_area = None

    def _confirm(self):
        """确认选择（右键）"""
        if self.selected_area:
            self.root.quit()
            self.root.destroy()

    def _cancel(self):
        """取消截图"""
        self.selected_area = None
        self.root.quit()
        self.root.destroy()


def grab_area(area: Tuple[int, int, int, int]) -> Image.Image:
    """截取指定区域

    Args:
        area: (x1, y1, x2, y2)

    Returns:
        PIL Image对象
    """
    x1, y1, x2, y2 = area
    # 使用ImageGrab截取区域
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    return img


def grab_fullscreen() -> Image.Image:
    """截取全屏"""
    return ImageGrab.grab()
