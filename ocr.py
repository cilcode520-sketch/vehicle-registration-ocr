import base64
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def extract_text(image_bytes: bytes) -> str:
    """用 Claude Vision 辨識行照圖片，回傳整理好的文字。"""
    try:
        b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
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
                            ),
                        },
                    ],
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ 辨識失敗：{e}"
