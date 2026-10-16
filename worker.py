import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from scraper import EnterpriseMarketScraper
from alerts import send_stock_alert_telegram, send_firebase_push_notification

load_dotenv()

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
scraper = EnterpriseMarketScraper()
semaphore = asyncio.Semaphore(5)

async def processar_unico_produto(prod: dict, loop: asyncio.AbstractEventLoop):
    async with semaphore:
        prod_id = prod["id"]
        url = prod["supplier_url"]
        old_price = float(prod["current_cost_usd"])
        prod_name = prod["product_name"]
        
        try:
            scraped_data = await loop.run_in_executor(None, scraper.fetch_product_data, url)
            if "error" in scraped_data:
                return

            new_price = scraped_data["price_usd"]
            in_stock = scraped_data["in_stock"]

            # 🚨 CONTINGÊNCIA CRÍTICA: Se faltar estoque, ativa o Auto-Swap e o Firebase Push
            if not in_stock:
                print(f"⚠️ Stockout detectado em: {prod_name}. Ativando protocolos...")
                
                # 1. Envia notificação Web Push via Firebase
                # Nota: Em produção, busque o fcm_token real do usuário na tabela public.profiles
                mock_fcm_token = "token_exemplo_fcm_usuario_supabase" 
                await loop.run_in_executor(
                    None, send_firebase_push_notification, mock_fcm_token, prod_name, 
                    "Produto esgotado no fornecedor original! Iniciando busca de contingência..."
                )
                
                # 2. Executa o Auto-Swap para achar link alternativo
                alternative_url = await loop.run_in_executor(None, scraper.find_alternative_supplier_aliexpress, prod_name)
                
                if alternative_url:
                    # Atualiza o banco do Supabase substituindo a URL do fornecedor de forma transparente
                    supabase.table("monitored_products").update({
                        "supplier_url": alternative_url,
                        "last_checked_at": "now()"
                    }).eq("id", prod_id).execute()
                    
                    await loop.run_in_executor(
                        None, send_firebase_push_notification, mock_fcm_token, prod_name, 
                        "Sucesso! Fornecedor substituído automaticamente pelo AliExpress."
                    )
                else:
                    # Se não achar alternativa, dispara o alerta crítico no Telegram para o lojista pausar anúncios
                    platform = "shopee" if "shopee.com" in url else "aliexpress"
                    await loop.run_in_executor(None, send_stock_alert_telegram, prod_name, url, platform)
                return

            # Atualização regular de preços
            if new_price != old_price:
                supabase.table("monitored_products").update({"current_cost_usd": new_price, "last_checked_at": "now()"}).eq("id", prod_id).execute()
                supabase.table("price_history").insert({"product_id": prod_id, "old_cost_usd": old_price, "new_cost_usd": new_price}).execute()
            else:
                supabase.table("monitored_products").update({"last_checked_at": "now()"}).eq("id", prod_id).execute()

        except Exception as e:
            print(f"💥 Erro no produto {prod_id}: {str(e)}")

async def main_worker_loop():
    loop = asyncio.get_running_loop()
    print("🚀 [Robo] DropSync Worker (FCM + Auto-Swap) Rodando...")
    while True:
        try:
            response = supabase.table("monitored_products").select("*").eq("is_active", True).order("last_checked_at").limit(20).execute()
            if response.data:
                tarefas = [processar_unico_produto(p, loop) for p in response.data]
                await asyncio.gather(*tarefas)
            await asyncio.sleep(60)
        except Exception as e:
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main_worker_loop())
