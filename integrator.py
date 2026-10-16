import os

def calculate_brazilian_taxes(cost_usd: float, margin_percent: float, is_national: bool = False) -> dict:
    """
    Calcula os impostos de nacionalizacao. Se for fornecedor nacional,
    ignora as taxas de importacao do Remessa Conforme e calcula o custo direto.
    """
    dollar_env = os.environ.get("USD_BRL_QUOTE")
    usd_brl_quote = float(dollar_env) if dollar_env else 5.65
    
    custo_base_brl = cost_usd * usd_brl_quote
    aliquota_icms = 0.20  # 20% padrao
    
    if is_national:
        # Fornecedor do Brasil: Sem taxas aduaneiras ou ICMS de importacao por dentro
        custo_nacionalizado = custo_base_brl
        imposto_importacao = 0.0
        icms_pago = 0.0
    else:
        # Fornecedor Internacional (Remessa Conforme)
        if custo_base_brl < (50.0 * usd_brl_quote):
            custo_nacionalizado = custo_base_brl / (1.0 - aliquota_icms)
            imposto_importacao = 0.0
            icms_pago = custo_nacionalizado * aliquota_icms
        else:
            aliquota_ii = 0.60
            base_ii = custo_base_brl * (1.0 + aliquota_ii)
            custo_nacionalizado = base_ii / (1.0 - aliquota_icms)
            imposto_importacao = custo_base_brl * aliquota_ii
            icms_pago = custo_nacionalizado * aliquota_icms

    # Precificacao final da loja com base na margem do lojista
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
