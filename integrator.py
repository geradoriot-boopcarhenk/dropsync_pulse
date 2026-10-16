import os

def calculate_brazilian_taxes(cost_usd: float, margin_percent: float) -> dict:
    """
    Calcula os impostos de nacionalizacao (Remessa Conforme) e define as metricas 
    de precificacao da loja com fallbacks seguros contra variaveis de ambiente nulas.
    """
    # Fallback seguro: se a variavel de ambiente nao existir ou for vazia, assume 5.65
    dollar_env = os.environ.get("USD_BRL_QUOTE")
    usd_brl_quote = float(dollar_env) if dollar_env else 5.65
    
    # Converte o custo original para Reais
    custo_base_brl = cost_usd * usd_brl_quote
    
    # Regras fiscais do Remessa Conforme (ICMS por dentro)
    aliquota_icms = 0.20  # 20% padrao
    
    if custo_base_brl < (50.0 * usd_brl_quote):
        # Isencao de Imposto de Importacao, incide apenas ICMS por dentro
        custo_nacionalizado = custo_base_brl / (1.0 - aliquota_icms)
        imposto_importacao = 0.0
        icms_pago = custo_nacionalizado * aliquota_icms
    else:
        # Acima de 50 USD incide 60% de Imposto de Importacao + ICMS por dentro
        aliquota_ii = 0.60
        base_ii = custo_base_brl * (1.0 + aliquota_ii)
        custo_nacionalizado = base_ii / (1.0 - aliquota_icms)
        imposto_importacao = custo_base_brl * aliquota_ii
        icms_pago = custo_nacionalizado * aliquota_icms

    # Calculo do Preco de Venda com base na margem estipulada pelo lojista
    fator_margem = 1.0 + (margin_percent / 100.0)
    preco_venda_final = custo_nacionalizado * fator_margem
    lucro_liquido = preco_venda_final - custo_nacionalizado

    return {
        "custo_nacionalizado_total": round(custo_nacionalizado, 2),
        "preco_venda_final_loja": round(preco_venda_final, 2),
        "lucro_liquido_venda": round(lucro_liquido, 2),
        "imposto_importacao_brl": round(imposto_importacao, 2),
        "icms_brl": round(icms_pago, 2)
    }
