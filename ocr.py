import io
import os

import google.generativeai as genai
from PIL import Image

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT = (
    "這是一張台灣的行車執照（行照）。\n"
    "請辨識所有欄位，嚴格按照以下格式輸出，每行一個欄位，不要加任何多餘說明：\n\n"
    "牌照號碼：\n"
    "車主：\n"
    "地址：\n"
    "廠牌型式：\n"
    "引擎號碼：\n"
    "車身號碼：\n"
    "顏色：\n"
    "排氣量：\n"
    "發照日期：\n"
    "出廠年月：\n"
    "換補照日期：\n"
    "有效日期：\n"
    "管轄編號：\n\n"
    "若某欄位圖片中看不到，填「—」。"
)


def extract_text(image_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([img, PROMPT])
        return response.text
    except Exception as e:
        return f"⚠️ 辨識失敗：{e}"
