"""
OCR引擎封装 - 使用RapidOCR
"""

import os
import sys
from typing import Optional, Tuple
from pathlib import Path

# RapidOCR导入（需要安装rapidocr_onnxruntime）
try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    RapidOCR = None
    print("警告: 未安装 rapidocr_onnxruntime，请运行: pip install rapidocr-ocr")


class OCREngine:
    """OCR引擎单例封装"""

    _instance: Optional['OCREngine'] = None
    _ocr_engine = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, lang: str = "ch", model_path: Optional[str] = None):
        """初始化OCR引擎

        Args:
            lang: 语言代码，ch(中文)/en(英文)/mixed(中英混合)
            model_path: 自定义模型路径，None使用默认自动下载
        """
        if self._ocr_engine is not None:
            return

        if RapidOCR is None:
            raise ImportError("请先安装: pip install rapidocr-ocr")

        # RapidOCR会自动下载模型，不需要提前指定详细路径
        # model_path参数仅用于指定自定义模型目录
        kwargs = {'use_angle_cls': True}
        if model_path:
            # 自定义模型目录下应该有ppocr_v3子目录
            kwargs['det_model_path'] = os.path.join(model_path, "det.onnx")
            kwargs['cls_model_path'] = os.path.join(model_path, "cls.onnx")
            kwargs['rec_model_path'] = os.path.join(model_path, "rec.onnx")
            kwargs['dict_path'] = os.path.join(model_path, "ppocr_dict_v3.txt")

        self._ocr_engine = RapidOCR(**kwargs)
        self.lang = lang

        if model_path:
            print(f"OCR引擎初始化完成，自定义模型路径: {model_path}")
        else:
            print(f"OCR引擎初始化完成，使用内置模型（自动下载）")

    def recognize(self, image) -> str:
        """识别图像中的文字

        Args:
            image: PIL Image对象或numpy数组

        Returns:
            识别出的纯文本
        """
        if self._ocr_engine is None:
            raise RuntimeError("OCR引擎未初始化")

        try:
            # RapidOCR接受numpy数组或文件路径
            import numpy as np
            if hasattr(image, 'convert'):
                # PIL Image转numpy
                image_np = np.array(image.convert('RGB'))
            else:
                image_np = image

            result, _ = self._ocr_engine(image_np)

            if not result or len(result) == 0:
                return ""

            # RapidOCR返回格式: [[bbox, text, score], ...]
            # 提取所有text文本
            texts = []
            for item in result:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    text = item[1]  # 第二个元素是文本
                    if text and isinstance(text, str):
                        texts.append(text.strip())

            if not texts:
                return ""

            # 返回所有识别文本，用换行分隔
            return "\n".join(texts).strip()

        except Exception as e:
            print(f"OCR识别出错: {e}")
            return ""

    def is_ready(self) -> bool:
        """检查引擎是否就绪"""
        return self._ocr_engine is not None


# 全局OCR引擎实例（延迟初始化）
_ocr_instance = None


def get_ocr_engine(lang: str = "ch", model_path: Optional[str] = None) -> OCREngine:
    """获取OCR引擎实例（单例）"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCREngine(lang=lang, model_path=model_path)
    return _ocr_instance
