import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Inicializa o cliente usando a service role key administrativa
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Erro: Variáveis do Supabase ausentes no .env.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def seed_database():
    print("========================================================")
    print("🚀 INICIANDO MIGRAÇÃO E ALIMENTAÇÃO DO BANCO (SEED)     ")
    print("========================================================")

    # 1. POPULAR OS PLANOS SAAS BASE
    print("📦 1. Verificando e populando planos SaaS...")
    planos = [
        {"id": 1, "name": "Starter", "price_brl": 149.00, "max_monitored_products": 20, "check_interval_hours": 12, "has_auto_swap_supplier": False},
        {"id": 2, "name": "Pro Scale", "price_brl": 299.00, "max_monitored_products": 100, "check_interval_hours": 4, "has_auto_swap_supplier": True},
        {"id": 3, "name": "Enterprise Premium", "price_brl": 499.00, "max_monitored_products": 500, "check_interval_hours": 1, "has_auto_swap_supplier": True}
    ]
    
    for plano in planos:
        try:
            # Tenta inserir; se já existir, faz o upsert
            supabase.table("saas_plans").upsert(plano).execute()
            print(f"   ✅ Plano '{plano['name']}' sincronizado.")
        except Exception as e:
            print(f"   ⚠️ Falha no plano {plano['name']}: {str(e)}")

    print("-" * 60)

    # 2. CRIAR UM PERFIL MOCK PARA TESTES LOCAIS/HOMOLOGAÇÃO
    # Usamos o UUID padrão (zeros) que mapeamos no frontend para testes sem autenticação complexa
    print("👤 2. Configurando perfil mock de teste...")
    perfil_mock = {
        "id": "00000000-0000-0000-0000-000000000000",
        "store_url": "https://minhaloja-fedora.com.br",
        "plan_id": 2,  # Vincula ao plano Pro Scale
        "subscription_status": "trial"
    }
    try:
        supabase.table("profiles").upsert(perfil_mock).execute()
        print("   ✅ Perfil administrativo mock inserido.")
    except Exception as e:
        print(f"   ⚠️ Falha ao inserir perfil mock: {str(e)}")

    print("-" * 60)

    # 3. POPULAR PRODUTOS DE EXEMPLO PARA O ROBÔ RASCAR
    print("🛒 3. Populando produtos de teste para a fila do Scraper...")
    produtos_mock = [
        {
            "id": 991,
            "user_id": "00000000-0000-0000-0000-000000000000",
            "product_name": "Fone de Ouvido M10 Bluetooth",
            "supplier_url": "https://shopee.com.br",
            "current_cost_usd": 4.50,
            "desired_margin_percent": 40.0,
            "is_active": True
        },
        {
            "id": 992,
            "user_id": "00000000-0000-0000-0000-000000000000",
            "product_name": "Parafusadeira de Impacto 48V",
            "supplier_url": "https://aliexpress.com",
            "current_cost_usd": 22.10,
            "desired_margin_percent": 35.0,
            "is_active": True
        }
    ]

    for prod in produtos_mock:
        try:
            supabase.table("monitored_products").upsert(prod).execute()
            print(f"   ✅ Produto '{prod['product_name']}' injetado na fila.")
        except Exception as e:
            print(f"   ⚠️ Falha no produto {prod['product_name']}: {str(e)}")

    print("========================================================")
    print("🎉 MIGRAÇÃO CONCLUÍDA! Seu banco está pronto para uso.")
    print("========================================================")

if __name__ == "__main__":
    seed_database()
