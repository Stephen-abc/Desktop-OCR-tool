"""
热键监听模块
"""

import threading
from pynput import keyboard, mouse
from typing import Callable, Optional
from config import load_config


class HotkeyManager:
    """全局热键管理器"""

    def __init__(self):
        self.config = load_config()
        self._hotkey = self.config.get("hotkey", "Ctrl+Alt+S")
        self._hotkey_id = None
        self._listener = None
        self._mouse_listener = None
        self._running = False
        self._callback = None
        self._lock = threading.Lock()

    def set_callback(self, callback: Callable):
        """设置热键触发回调"""
        self._callback = callback

    def start(self):
        """启动热key监听"""
        if self._running:
            return

        self._running = True

        # 启动键盘监听
        keyboard_thread = threading.Thread(target=self._run_keyboard, daemon=True)
        keyboard_thread.start()

        # 启动鼠标监听（右键）
        mouse_thread = threading.Thread(target=self._run_mouse, daemon=True)
        mouse_thread.start()

        print(f"热键监听已启动: {self._hotkey} (右键也可触发)")

    def stop(self):
        """停止监听"""
        self._running = False
        if self._listener:
            self._listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()

    def update_hotkey(self, new_hotkey: str):
        """更新热key"""
        old_hotkey = self._hotkey
        self._hotkey = new_hotkey

        # 重启监听器
        if self._running:
            if self._listener:
                self._listener.stop()
            keyboard_thread = threading.Thread(target=self._run_keyboard, daemon=True)
            keyboard_thread.start()

        print(f"热键已更新: {old_hotkey} -> {new_hotkey}")

    def _run_keyboard(self):
        """运行键盘监听器"""
        try:
            # 解析热键字符串为pynput格式
            hotkey = self._parse_hotkey(self._hotkey)

            def on_activate():
                if self._callback:
                    self._callback()

            with keyboard.GlobalHotKeys({hotkey: on_activate}) as listener:
                self._listener = listener
                listener.join()

        except Exception as e:
            print(f"热key监听启动失败: {e}")

    def _run_mouse(self):
        """运行鼠标监听（右键）"""
        try:
            def on_click(x, y, button, pressed):
                if self._running and pressed and button == mouse.Button.right:
                    # 右键按下触发
                    if self._callback:
                        self._callback()

            with mouse.Listener(on_click=on_click) as listener:
                self._mouse_listener = listener
                listener.join()

        except Exception as e:
            print(f"鼠标监听失败: {e}")

    def _parse_hotkey(self, hotkey_str: str) -> str:
        """将热key字符串转换为pynput格式

        例如:
        "Ctrl+Alt+S" -> "<ctrl>+<alt>+s"
        "Ctrl+Shift+S" -> "<ctrl>+<shift>+s"
        """
        parts = hotkey_str.lower().split('+')
        parsed = []

        for part in parts:
            part = part.strip()
            if part == 'ctrl':
                parsed.append('<ctrl>')
            elif part == 'alt':
                parsed.append('<alt>')
            elif part == 'shift':
                parsed.append('<shift>')
            elif part == 'win':
                parsed.append('<cmd>')
            else:
                # 单个字母或功能键
                parsed.append(part.lower())

        return '+'.join(parsed)

    def is_valid_hotkey(self, hotkey_str: str) -> bool:
        """验证热key格式是否有效"""
        if not hotkey_str:
            return False

        parts = hotkey_str.split('+')
        if len(parts) > 3:
            return False  # 最多3个修饰键+1个主键

        # 检查每个部分
        valid_modifiers = {'ctrl', 'alt', 'shift', 'win'}
        main_key_found = False

        for part in parts:
            part_lower = part.strip().lower()
            if part_lower in valid_modifiers:
                continue
            elif len(part_lower) == 1 and part_lower.isalpha():
                main_key_found = True
            else:
                return False

        return main_key_found
