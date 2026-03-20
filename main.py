import os

from fastapi import FastAPI, Request, Header, HTTPException
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, ImageMessageContent
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
)

from ocr import extract_text

# ── 環境變數 ──────────────────────────────────────────────
CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

app = FastAPI()


# ── 健康檢查 ──────────────────────────────────────────────
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

    try:
        events = parser.parse(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(
            event.message, ImageMessageContent
        ):
            handle_image(event)

    return "OK"


def handle_image(event: MessageEvent):
    """下載圖片 → OCR → 回傳文字給使用者"""
    with ApiClient(configuration) as api_client:
        blob_api = MessagingApiBlob(api_client)
        line_bot_api = MessagingApi(api_client)

        # 從 LINE 伺服器下載圖片
        image_bytes = blob_api.get_message_content(event.message.id)

        # OCR 辨識
        text = extract_text(image_bytes)

        reply = (
            f"✅ 行照辨識結果：\n\n{text}"
            if text.strip()
            else "⚠️ 無法辨識文字，請確認圖片清晰且光線充足後重新拍攝。"
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)],
            )
        )
