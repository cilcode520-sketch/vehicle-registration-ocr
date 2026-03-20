import os
import requests

from fastapi import FastAPI, Request, Header, HTTPException
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, ImageMessageContent
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
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


def download_image(message_id: str) -> bytes:
    """直接用 HTTP 從 LINE 下載圖片"""
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.content


def handle_image(event: MessageEvent):
    """下載圖片 → OCR → 回傳文字給使用者"""
    image_bytes = download_image(event.message.id)
    text = extract_text(image_bytes)

    reply = (
        f"✅ 行照辨識結果：\n\n{text}"
        if text.strip()
        else "⚠️ 無法辨識文字，請確認圖片清晰且光線充足後重新拍攝。"
    )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=event.source.user_id,
                messages=[TextMessage(text=reply)],
            )
        )
