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
                                "這是一張台灣的行車執照（行照）。"
                                "請將圖片中所有欄位的文字完整辨識出來，"
                                "以「欄位名稱：內容」的格式逐行列出，不要遺漏任何資訊。"
                            ),
                        },
                    ],
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ 辨識失敗：{e}"
