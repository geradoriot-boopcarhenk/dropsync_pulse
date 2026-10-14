import requests

TOKEN = "8928861406:AAHMdtrqCevqNTP16yQ9Z4NvdC7ciD6-WmM"
CHAT_ID = "7782153304"

texto = (
    f"🚨 <b>[TESTE DE DISPARO] DROPSYNC PULSE</b>\n\n"
    f"📦 <b>Produto:</b> Parafusadeira Profissional 48V\n"
    f"📉 <b>Preço Antigo:</b> R$ 123.50\n"
    f"⚡ <b>Novo Preço de Custo:</b> R$ 150.00\n"
    f"📊 <b>Status:</b> 🔥 Variação detectada no teste!"
)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "parse_mode": "HTML", "text": texto}

try:
    res = requests.post(url, json=payload, timeout=10)
    print(f"📡 Resposta do Telegram: {res.json()}")
except Exception as e:
    print(f"❌ Erro: {e}")
