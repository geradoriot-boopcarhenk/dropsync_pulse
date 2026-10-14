# ~/dropsync_pulse/main.py
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from supabase import create_client, Client

# Realiza a importacao segura do modulo de faturamento
from payment import payment_router

load_dotenv()

app = FastAPI(
    title="DropSync Pulse API",
    description="Core Enterprise Gateway para o ecossistema DropSync SaaS",
    version="1.0.0"
)

# Registra formalmente as rotas do Webhook do Asaas
app.include_router(payment_router)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Variáveis de ambiente do Supabase ausentes.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ProductCreate(BaseModel):
    user_id: str = None
    product_name: str
    supplier_url: str
    desired_margin_percent: float = Field(default=30.0, ge=1.0)
    store_product_id: str = None

class ProductResponse(BaseModel):
    id: int
    product_name: str
    supplier_url: str
    current_cost_usd: float
    desired_margin_percent: float
    is_active: bool

@app.get("/", tags=["Health"])
def health_check():
    try:
        supabase.table("saas_plans").select("id").limit(1).execute()
        return {"status": "online", "database_connection": "estavel", "environment": "Fedora Linux"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products/", response_model=List[ProductResponse], status_code=status.HTTP_201_CREATED, tags=["Produtos"])
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
