from flask import Flask, request
import requests
import json
import os

import sys
# sys.exit("🔴 Encerrando app.py para confirmar execução no Render")

app = Flask(__name__)

# === Caminho absoluto do diretório atual ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Leitura dos arquivos .txt ===
with open(os.path.join(BASE_DIR, "VERIFY_TOKEN.txt"), "r") as f:
    VERIFY_TOKEN = f.read().strip()

with open(os.path.join(BASE_DIR, "ACCESS_TOKEN.txt"), "r") as f:
    ACCESS_TOKEN = f.read().strip()

with open(os.path.join(BASE_DIR, "PHONE_NUMBER_ID.txt"), "r") as f:
    PHONE_NUMBER_ID = f.read().strip()

# === Verificação do Webhook (GET) ===
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Prints de debug para inspecionar o problema
    print("📌 Token recebido via GET:", repr(token))
    print("📌 Token carregado do arquivo:", repr(VERIFY_TOKEN))
    print("📌 Tipo do token recebido:", type(token))
    print("📌 Tipo do token do arquivo:", type(VERIFY_TOKEN))

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado com sucesso!")
        return challenge, 200
    else:
        print("❌ Token de verificação inválido!")
        return "Token inválido", 403

# === Recebimento de Mensagens (POST) ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Dados recebidos:", json.dumps(data, indent=2))

    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
            phone_number = message_data["from"]
            text = message_data["text"]["body"]

            print(f"📥 Mensagem de {phone_number}: {text}")

            send_message(phone_number, "Olá! A Sullato agradece o seu contato. Em que posso te ajudar?")
    except Exception as e:
        print("⚠️ Erro ao processar mensagem:", str(e))

    return "ok", 200

# === Envio de Mensagem de Resposta ===
def send_message(phone_number, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Resposta enviada:", response.status_code, response.text)

Comentando sys.exit para liberar execução no Render


# === Inicialização do Servidor Flask ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
