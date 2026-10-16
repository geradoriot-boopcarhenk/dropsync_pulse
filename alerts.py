import os
import httpx
import firebase_admin
from firebase_admin import credentials, messaging

TELEGRAM_BOT_TOKEN = "8928861406:AAHMdtrqCevqNTP16yQ9Z4NvdC7ciD6-WmM"
TELEGRAM_CHAT_ID = "7782153304"

# Inicializa o SDK Administrativo do Firebase de forma segura (Singleton)
FIREBASE_CRED_PATH = os.path.expanduser("~/dropsync_pulse/firebase-credentials.json")

if not firebase_admin._apps and os.path.exists(FIREBASE_CRED_PATH):
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

def send_firebase_push_notification(fcm_token: str, product_name: str, message_body: str):
    """Dispara uma notificação push via FCM (V1) para o dispositivo do lojista."""
    if not fcm_token or not firebase_admin._apps:
        return False
    
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"⚡ DropSync Pulse: {product_name}",
            body=message_body,
        ),
        token=fcm_token,
    )
    try:
        messaging.send(message)
        print(f"📱 [FCM] Push disparado com sucesso para o token: {fcm_token[:10]}...")
        return True
    except Exception as e:
        print(f"❌ [FCM] Falha ao enviar push: {str(e)}")
        return False

def send_stock_alert_telegram(product_name: str, supplier_url: str, platform: str) -> bool:
    """Dispara uma notificação push imediata via bot do Telegram informando a escassez."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "seu_token_do_bot_telegram":
        return False
        
    mensagem = (
        f"🚨 *PRODUTO ESGOTADO NO FORNECEDOR!*\n\n"
        f"📦 *Produto:* {product_name}\n"
        f"🌐 *Origem:* {platform.upper()}\n"
        f"🔗 *Link do Fornecedor:* [Acessar Fonte]({supplier_url})\n\n"
        f"⚠️ *Ação Recomendada:* Pause seus anúncios ou mude de fornecedor agora!"
    )
    
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        with httpx.Client(timeout=6.0) as client:
            response = client.post(url, json=payload)
            return response.status_code == 200
    except Exception:
        return False
