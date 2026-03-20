import io
import re
import pytesseract
from PIL import Image, ImageFilter, ImageOps


def preprocess(image_bytes: bytes) -> Image.Image:
    """將圖片轉灰階、銳化，提高 Tesseract 辨識率。"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 放大兩倍（小圖 OCR 效果較差）
    w, h = img.size
    if w < 1200:
        img = img.resize((w * 2, h * 2), Image.LANCZOS)

    # 灰階 → 銳化
    img = ImageOps.grayscale(img)
    img = img.filter(ImageFilter.SHARPEN)

    return img


def extract_text(image_bytes: bytes) -> str:
    """
    從圖片 bytes 中辨識行照文字。
    回傳清理後的純文字字串；失敗時回傳錯誤提示。
    """
    try:
        img = preprocess(image_bytes)
        raw = pytesseract.image_to_string(
            img,
            lang="chi_tra+eng",
            config="--psm 6",  # 假設為整齊區塊文字
        )
        return _clean(raw)
    except Exception as e:
        return f"⚠️ OCR 辨識失敗：{e}"


def _clean(text: str) -> str:
    """移除多餘空白行與行首行尾空白。"""
    lines = [line.strip() for line in text.splitlines()]
    # 過濾掉完全空白的行，但保留有內容的行
    lines = [line for line in lines if line]
    return "\n".join(lines)
