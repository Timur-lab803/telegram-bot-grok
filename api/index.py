import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.grok.ai/v1/generate")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set")
if not GROK_API_KEY:
    print("Warning: GROK_API_KEY not set; Grok calls will fail")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print("send_message error:", e)

def call_grok(prompt):
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "grok-4", "input": prompt, "options": {"max_tokens": 512, "temperature": 0.6}}
    try:
        r = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        j = r.json()
        if isinstance(j, dict):
            if 'output' in j and isinstance(j['output'], str):
                return j['output']
            if 'choices' in j and len(j['choices'])>0:
                first = j['choices'][0]
                if isinstance(first, dict):
                    if 'text' in first:
                        return first['text']
                    if 'message' in first and isinstance(first['message'], dict):
                        return first['message'].get('content','')
        return str(j)
    except Exception as e:
        return f"Error calling Grok API: {e}"

WELCOME = "👋 Привет! Я дружелюбный бот, интегрированный с Grok-4. Задай любой вопрос — я постараюсь помочь."

@app.route("/", methods=["GET"])
def root():
    return "Grok Telegram webhook ready."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    message = data.get("message") or data.get("edited_message")
    if not message:
        return jsonify({"ok": True})
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    if not text:
        return jsonify({"ok": True})
    if text.strip().startswith("/start"):
        send_message(chat_id, WELCOME)
        return jsonify({"ok": True})
    if text.strip().startswith("/help"):
        send_message(chat_id, "Напиши любой вопрос — я передам его Grok и пришлю ответ. Будь вежлив :)")
        return jsonify({"ok": True})
    send_message(chat_id, "Запрос получен. Обращаюсь к Grok...")
    answer = call_grok(text)
    if len(answer) > 4000:
        for i in range(0, len(answer), 3500):
            send_message(chat_id, answer[i:i+3500])
    else:
        send_message(chat_id, answer)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
