# ~/dropsync_pulse/test_telegram.py
import os
from dotenv import load_dotenv
from alerts import send_stock_alert_telegram

# Garante a carga das credenciais do arquivo .env atualizado
load_dotenv()

print("⏳ Disparando notificação push de teste para o seu Telegram...")

# Dispara a função oficial de alertas do seu ecossistema
sucesso = send_stock_alert_telegram(
    product_name="Smartwatch Ultra Pro Max", 
    supplier_url="https://shopee.com.br", 
    platform="shopee"
)

if sucesso:
    print("✅ Sucesso absoluto! Olhe a tela do seu celular!")
else:
    print("❌ Falha no envio. Verifique se o bot @dropsync_pulse_hz_bot está iniciado ou confira as chaves no .env.")
