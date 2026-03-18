"""
配置管理模块
"""

import json
import os
from typing import Dict, Any

CONFIG_DIR = os.path.expanduser("~/.ocr_tool")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "hotkey": "Ctrl+Alt+S",
    "ocr_lang": "ch",  # ch/en/mixed
    "auto_start": False,
    "show_notification": True,
    "model_path": None  # None表示使用默认路径
}


def ensure_config_dir() -> None:
    """确保配置目录存在"""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """加载配置，如果不存在则创建默认配置"""
    ensure_config_dir()

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 合并缺失的默认值
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        return config
    except Exception as e:
        print(f"加载配置失败，使用默认配置: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """保存配置"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_config_path() -> str:
    """获取配置目录路径"""
    return CONFIG_DIR
