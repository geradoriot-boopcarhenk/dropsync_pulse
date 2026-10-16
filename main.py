import os
from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="DropSync Pulse API", version="1.0.0")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SCHEMAS PYDANTIC ---
class ProductCreate(BaseModel):
    user_id: str
    product_name: str
    supplier_url: str
    desired_margin_percent: float

class ProductResponse(BaseModel):
    id: int
    user_id: str
    product_name: str
    supplier_url: str
    desired_margin_percent: float
    current_cost_usd: Optional[float]
    is_active: bool

# --- ROTAS DA API ---

@app.post("/products", response_model=List[ProductResponse], status_code=status.HTTP_201_CREATED, tags=["Produtos"])
def create_monitored_product(product: ProductCreate):
    payload = {
        "user_id": product.user_id,
        "product_name": product.product_name,
        "supplier_url": product.supplier_url,
        "desired_margin_percent": product.desired_margin_percent,
        "current_cost_usd": 0.00
    }
    try:
        response = supabase.table("monitored_products").insert(payload).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/asaas", status_code=status.HTTP_200_OK, tags=["Webhooks"])
def receive_asaas_webhook(payload: dict, asaas_access_token: Optional[str] = Header(None)):
    """Recebe confirmações, atrasos e cancelamentos do Asaas para gerenciar licenças."""
    expected_token = os.environ.get("ASAAS_WEBHOOK_TOKEN")
    if expected_token and asaas_access_token != expected_token:
        raise HTTPException(status_code=401, detail="Token de autenticacao invalido")

    evento = payload.get("event")
    payment_data = payload.get("payment", {})
    
    # Mapeamento de Clientes: O Asaas envia o 'customer'. Na produção, você cruza o customer_id com o usuário.
    # Para o fluxo de homologação, usaremos o ID padrão do lojista admin ou capturamos do metadado.
    user_id = "00000000-0000-0000-0000-000000000000" 

    try:
        if evento in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            # Ativação imediata da licença
            supabase.table("profiles").update({"subscription_status": "active"}).eq("id", user_id).execute()
            return {"status": "success", "message": "Licenca ATIVADA via confirmacao de pagamento."}

        elif evento in ["PAYMENT_OVERDUE", "PAYMENT_CHARGEBACK_REQUESTED"]:
            # Cliente atrasou o pagamento da mensalidade (Inadimplente)
            supabase.table("profiles").update({"subscription_status": "overdue"}).eq("id", user_id).execute()
            return {"status": "success", "message": "Licenca SUSPENSA por atraso de pagamento."}

        elif evento in ["PAYMENT_DELETED", "BILLING_CANCELED"]:
            # Cliente cancelou a assinatura ou removeu a cobrança
            supabase.table("profiles").update({"subscription_status": "canceled"}).eq("id", user_id).execute()
            return {"status": "success", "message": "Licenca BLOQUEADA por cancelamento definitivo."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar estado da licenca: {str(e)}")
        
    return {"status": "ignored", "message": f"Evento {evento} recebido sem regras de bloqueio."}

