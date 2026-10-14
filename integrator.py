# ~/dropsync_pulse/integrator.py
import httpx

def get_live_usd_exchange_rate() -> float:
    """Busca o câmbio atualizado do dólar comercial."""
    url = "https://awesomeapi.com.br"
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                return float(data["USDBRL"]["bid"])
    except Exception:
        return 5.65  # Fallback dinâmico caso a API externa falhe

def calculate_brazilian_taxes(cost_usd: float, margin_percent: float) -> dict:
    """Processa a arquitetura tributária completa do Remessa Conforme."""
    exchange_rate = get_live_usd_exchange_rate()
    cost_brl_base = cost_usd * exchange_rate
    
    # 1. IOF sobre transações internacionais (4.38%)
    iof = cost_brl_base * 0.0438
    
    # 2. Imposto de Importação Federal (Alíquota escalonada)
    if cost_usd <= 50.0:
        imposto_importacao = cost_brl_base * 0.20
    else:
        imposto_importacao = cost_brl_base * 0.60
        
    # 3. ICMS Estadual Calculado 'Por Dentro' (17%)
    aliquota_icms = 0.17
    base_calculo_icms = (cost_brl_base + imposto_importacao) / (1 - aliquota_icms)
    icms = base_calculo_icms * aliquota_icms
    
    # Consolidação de custos e preço de gôndola Shopify/Yampi
    total_cost_brl = cost_brl_base + iof + imposto_importacao + icms
    venda_sugerida_brl = total_cost_brl * (1 + (margin_percent / 100))
    lucro_liquido_brl = venda_sugerida_brl - total_cost_brl
    
    return {
        "cotacao_dolar_utilizada": exchange_rate,
        "custo_brl_puro": round(cost_brl_base, 2),
        "imposto_remessa_federal": round(imposto_importacao, 2),
        "icms_estadual": round(icms, 2),
        "custo_nacionalizado_total": round(total_cost_brl, 2),
        "preco_venda_final_loja": round(venda_sugerida_brl, 2),
        "lucro_liquido_venda": round(lucro_liquido_brl, 2)
    }
