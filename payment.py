# ~/dropsync_pulse/payment.py
import os
from fastapi import APIRouter, Request, HTTPException, Header, status
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Instancia o roteador com a sintaxe correta
payment_router = APIRouter(prefix="/v1/webhooks", tags=["Faturamento Asaas"])

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
ASAAS_WEBHOOK_TOKEN = os.environ.get("ASAAS_WEBHOOK_TOKEN")

@payment_router.post("/asaas")
async def receber_webhook_asaas(request: Request, asaastoken: str = Header(None)):
    if not asaastoken or asaastoken != ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")
    try:
        payload = await request.json()
        evento = payload.get("event")
        payment_data = payload.get("payment", {})
        user_uuid = payment_data.get("externalReference")
        
        if evento in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            if user_uuid:
                supabase.table("profiles").update({"subscription_status": "active"}).eq("id", user_uuid).execute()
                return {"status": "sucesso", "mensagem": "Assinatura ativada"}
        return {"status": "recebido"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
