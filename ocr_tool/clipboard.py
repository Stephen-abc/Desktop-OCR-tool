"""
剪贴板操作模块
"""

import platform
from typing import Tuple

# Windows上优先使用tkinter避免剪贴板冲突
if platform.system() == 'Windows':
    try:
        import tkinter as tk
        _root = None

        def _get_root():
            global _root
            if _root is None:
                _root = tk.Tk()
                _root.withdraw()  # 隐藏窗口
            return _root

        def copy_text(text: str, max_retries: int = 3) -> Tuple[bool, str]:
            """使用tkinter复制到剪贴板（Windows推荐）"""
            for attempt in range(max_retries):
                try:
                    root = _get_root()
                    root.clipboard_clear()
                    root.clipboard_append(text)
                    root.update()  # 确保写入剪贴板
                    char_count = len(text)
                    return True, f"已复制{char_count}个字符"
                except Exception as e:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
                        continue
                    return False, f"复制失败: {e}"

        def get_clipboard_text() -> str:
            """使用tkinter获取剪贴板文本"""
            try:
                root = _get_root()
                return root.clipboard_get()
            except Exception:
                return ""

    except ImportError:
        # tkinter不可用，回退到pyperclip
        import pyperclip

        def copy_text(text: str, max_retries: int = 3) -> Tuple[bool, str]:
            """复制文本到剪贴板"""
            for attempt in range(max_retries):
                try:
                    pyperclip.copy(text)
                    char_count = len(text)
                    return True, f"已复制{char_count}个字符"
                except Exception as e:
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
                        continue
                    return False, f"复制失败: {e}"

        def get_clipboard_text() -> str:
            """获取剪贴板当前文本"""
            try:
                return pyperclip.paste()
            except Exception:
                return ""

else:
    #非Windows使用pyperclip
    import pyperclip

    def copy_text(text: str, max_retries: int = 3) -> Tuple[bool, str]:
        """复制文本到剪贴板"""
        for attempt in range(max_retries):
            try:
                pyperclip.copy(text)
                char_count = len(text)
                return True, f"已复制{char_count}个字符"
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.5)
                    continue
                return False, f"复制失败: {e}"

    def get_clipboard_text() -> str:
        """获取剪贴板当前文本"""
        try:
            return pyperclip.paste()
        except Exception:
            return ""


def is_clipboard_available() -> bool:
    """检查剪贴板是否可用"""
    try:
        get_clipboard_text()
        return True
    except Exception:
        return False
