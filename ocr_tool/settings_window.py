"""
设置窗口模块
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from config import load_config, save_config
from hotkey import HotkeyManager


class SettingsWindow:
    """设置窗口"""

    def __init__(self, hotkey_manager: HotkeyManager, on_save_callback: Optional[Callable] = None):
        self.hotkey_manager = hotkey_manager
        self.on_save_callback = on_save_callback
        self.window = None
        self.entries = {}
        self.current_config = load_config()

    def show(self):
        """显示设置窗口"""
        self._create_window()
        self._load_config_to_ui()
        self.window.mainloop()

    def _create_window(self):
        """创建窗口和控件"""
        self.window = tk.Tk()
        self.window.title("OCR工具设置")
        self.window.geometry("400x320")
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)

        # 居中显示
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # 主容器
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 热key设置
        hotkey_frame = ttk.LabelFrame(main_frame, text="快捷键设置", padding="10")
        hotkey_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(hotkey_frame, text="截图热键:").pack(anchor=tk.W)
        self.entries['hotkey'] = ttk.Entry(hotkey_frame, width=30)
        self.entries['hotkey'].pack(pady=(5, 10), fill=tk.X)

        # 热key验证按钮
        btn_frame = ttk.Frame(hotkey_frame)
        btn_frame.pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(btn_frame, text="验证热键", command=self._test_hotkey).pack(side=tk.LEFT, padx=(0, 5))

        # 帮助文字
        ttk.Label(hotkey_frame, text="格式示例: Ctrl+Alt+S, Ctrl+Shift+S, 支持右键触发",
                  foreground="gray", wraplength=350).pack(anchor=tk.W)

        # 2. OCR设置
        ocr_frame = ttk.LabelFrame(main_frame, text="OCR设置", padding="10")
        ocr_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ocr_frame, text="识别语言:").pack(anchor=tk.W)
        self.entries['ocr_lang'] = ttk.Combobox(
            ocr_frame,
            values=["ch", "en", "mixed"],
            state="readonly",
            width=28
        )
        self.entries['ocr_lang'].pack(pady=(5, 10), fill=tk.X)

        # 3. 其他设置
        other_frame = ttk.LabelFrame(main_frame, text="其他设置", padding="10")
        other_frame.pack(fill=tk.X)

        self.entries['show_notification'] = tk.BooleanVar()
        chk = ttk.Checkbutton(other_frame, text="显示托盘通知", variable=self.entries['show_notification'])
        chk.pack(anchor=tk.W, pady=5)

        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="保存", command=self._on_save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="恢复默认", command=self._on_reset).pack(side=tk.LEFT)

    def _load_config_to_ui(self):
        """将配置加载到UI控件"""
        config = self.current_config

        # 热key
        self.entries['hotkey'].delete(0, tk.END)
        self.entries['hotkey'].insert(0, config.get('hotkey', 'Ctrl+Alt+S'))

        # OCR语言
        lang = config.get('ocr_lang', 'ch')
        self.entries['ocr_lang'].set(lang)

        # 通知开关
        self.entries['show_notification'].set(config.get('show_notification', True))

    def _test_hotkey(self):
        """测试热key是否有效"""
        hotkey_str = self.entries['hotkey'].get().strip()
        if self.hotkey_manager.is_valid_hotkey(hotkey_str):
            messagebox.showinfo("验证通过", f"热键格式有效: {hotkey_str}")
        else:
            messagebox.showerror("验证失败", "热键格式无效，请检查输入")

    def _on_save(self):
        """保存设置"""
        try:
            # 验证热key
            hotkey = self.entries['hotkey'].get().strip()
            if not self.hotkey_manager.is_valid_hotkey(hotkey):
                messagebox.showerror("错误", "热键格式无效")
                return

            # 更新配置
            new_config = {
                'hotkey': hotkey,
                'ocr_lang': self.entries['ocr_lang'].get(),
                'show_notification': self.entries['show_notification'].get(),
                'auto_start': self.current_config.get('auto_start', False),
                'model_path': self.current_config.get('model_path', None)
            }

            # 保存到文件
            save_config(new_config)
            self.current_config = new_config

            # 通知主程序更新热key
            self.hotkey_manager.update_hotkey(hotkey)

            if self.on_save_callback:
                self.on_save_callback()

            messagebox.showinfo("成功", "设置已保存")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _on_cancel(self):
        """取消"""
        self.window.destroy()

    def _on_reset(self):
        """恢复默认"""
        if messagebox.askyesno("确认", "恢复默认设置？"):
            self.entries['hotkey'].delete(0, tk.END)
            self.entries['hotkey'].insert(0, 'Ctrl+Alt+S')
            self.entries['ocr_lang'].set('ch')
            self.entries['show_notification'].set(True)

    def _on_close(self):
        """窗口关闭事件"""
        self.window.destroy()
