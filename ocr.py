import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                PROMPT,
            ],
        )
        return response.text
    except Exception as e:
        return f"⚠️ 辨識失敗：{e}"
