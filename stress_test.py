import asyncio
import time
from worker import processar_unico_produto

async def simulate_heavy_load_on_worker():
    print("========================================================")
    print("🚀 INICIANDO TESTE DE ESTRESSE: MÓDULO ASSÍNCRONO SEMÁFORO")
    print("========================================================")
    
    # Criamos um lote simulado pesado de 50 produtos idênticos concorrentes
    mock_batch = []
    for i in range(1, 51):
        mock_batch.append({
            "id": i,
            "product_name": f"Produto de Carga Estresse {i}",
            "supplier_url": "https://shopee.com.br", # URL controlada
            "current_cost_usd": 15.00,
            "desired_margin_percent": 35.0
        })
        
    loop = asyncio.get_running_loop()
    start_time = time.time()
    
    print(f"📦 Injetando {len(mock_batch)} requisições simultâneas no loop assíncrono...")
    print("🚦 O semáforo deve limitar a execução estrita de 5 por vez em paralelo.")
    print("-" * 60)
    
    # Dispara a concorrência geral controlada por semáforo
    tarefas = [processar_unico_produto(p, loop) for p in mock_batch]
    await asyncio.gather(*tarefas)
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    print("-" * 60)
    
    # Se o semáforo funcionou, as tarefas executaram de maneira cadenciada com segurança
    print(f"✅ Teste Concluído! Duração Total: {total_duration:.2f} segundos.")
    print(f"🔥 Taxa de Vazão Controlada: ~{len(mock_batch)/total_duration:.2f} produtos/seg.")
    print("========================================================")

if __name__ == "__main__":
    asyncio.run(simulate_heavy_load_on_worker())
