import httpx

# URL pública da sua API FastAPI no Railway (mapeada para bater no endpoint de webhooks)
# Caso a porta interna 8000 não esteja exposta diretamente no domínio principal,
# você pode rodar este script dentro do "Console" do Railway usando localhost:8000
url_producao = "https://railway.app"
url_local_container = "http://localhost:8000/webhooks/asaas/"

# Token secreto configurado no seu ASAAS_WEBHOOK_TOKEN
headers = {
    "Content-Type": "application/json",
    "asaas-access-token": "seu_token_secreto"  # Substitua pelo token real do seu .env
}

# Dados simulando o pagamento da assinatura do lojista admin (UUID zerado)
payload = {
    "event": "PAYMENT_RECEIVED",
    "payment": {
        "id": "pay_992817263544",
        "customer": "cus_000000000000",
        "value": 299.00,
        "netValue": 296.00,
        "billingType": "PIX",
        "status": "RECEIVED",
        "confirmedDate": "2026-10-15"
    }
}

try:
    print("📡 Disparando simulação de Webhook do Asaas...")
    # Tenta bater na URL pública
    response = httpx.post(url_producao, json=payload, headers=headers, timeout=10.0)
    print(f"📊 Status Code (Nuvem): {response.status_code}")
    print(f"💬 Resposta: {response.text}")
except Exception as e:
    print(f"❌ Falha ao conectar na URL pública: {e}")
    print("💡 Dica: Se o domínio do Railway estiver fixado apenas na porta 8501 do Streamlit, entre no 'Console' do Railway e rode 'python test_webhook.py' apontando para http://localhost:8000/webhooks/asaas/")
