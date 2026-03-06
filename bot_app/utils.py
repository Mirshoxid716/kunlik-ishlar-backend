import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

print(f"DEBUG: Utils loaded BOT_TOKEN: {BOT_TOKEN[:10]}... CHANNEL_ID: {CHANNEL_ID}")

def send_to_telegram(text, reply_markup=None, chat_id=None):
    if not text:
        return None
        
    # Global truncation to prevent "text is too long" error
    if len(text) > 4000:
        text = text[:3900] + "...\n[Xabar juda uzun bo'lgani uchun qisqartirildi]"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id or CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    print(f"DEBUG: Sending to {payload['chat_id']}: {text[:100]}...")
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Telegram API Response: {response.status_code} - {response.text}")
        return response
    except Exception as e:
        print(f"Telegram API Request Exception: {e}")
        raise

def edit_telegram_markup(message_id, reply_markup=None, chat_id=None):
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found for editing message")
        return False
        
    chat_id = chat_id or CHANNEL_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error editing Telegram markup: {e}")
        return False
