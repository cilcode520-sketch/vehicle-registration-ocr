import os
import hashlib
import hmac
import base64

from fastapi import FastAPI, Request, Header, HTTPException
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage

from ocr import extract_text

# ── 環境變數 ──────────────────────────────────────────────
CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

app = FastAPI()


# ── 健康檢查（Railway 會 ping 這裡）───────────────────────
@app.get("/")
async def health():
    return {"status": "ok"}


# ── LINE Webhook ──────────────────────────────────────────
@app.post("/callback")
async def callback(
    request: Request,
    x_line_signature: str = Header(...),
):
    body = await request.body()

    # 驗證簽名，防止偽造請求
    try:
        events = parser.parse(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(
            event.message, ImageMessage
        ):
            await handle_image(event)

    return "OK"


async def handle_image(event: MessageEvent):
    """下載圖片 → OCR → 回傳文字給使用者"""
    # 從 LINE 伺服器下載圖片
    message_content = line_bot_api.get_message_content(event.message.id)
    image_bytes = b"".join(chunk for chunk in message_content.iter_content())

    # OCR 辨識
    text = extract_text(image_bytes)

    if text.strip():
        reply = f"✅ 行照辨識結果：\n\n{text}"
    else:
        reply = "⚠️ 無法辨識文字，請確認圖片清晰且光線充足後重新拍攝。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply),
    )
