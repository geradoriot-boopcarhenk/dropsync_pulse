import streamlit as str_mock  # Apenas para garantir imports basicos se houver dependencias
import streamlit as st
import os
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Inicialização segura do banco de dados na nuvem
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

st.set_page_config(page_title="DropSync Pulse Pro", page_icon="📡", layout="wide")

# Inicialização de Estados de Sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # Mantém logado para desenvolvimento ativo
if "user_id" not in st.session_state:
    # Captura um ID padrão de testes direto do banco
    try:
        res = supabase.table("profiles").select("id").limit(1).execute()
        st.session_state.user_id = res.data[0]["id"] if res.data else "00000000-0000-0000-0000-000000000000"
    except:
        st.session_state.user_id = "00000000-0000-0000-0000-000000000000"

# --- BARRA LATERAL (SIDEBAR) COM FORMULÁRIO DE CADASTRO CORRIGIDO ---
with st.sidebar:
    st.markdown(f"👤 **Logado como:**\n`{st.session_state.user_id[:8]}...`")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.write("---")
    
    st.subheader("📝 Cadastrar Novo Produto")
    with st.form("form_cadastro", clear_on_submit=True):
        nome_prod = st.text_input("Nome do Produto", placeholder="Ex: Ventilador Turbo Portátil")
        url_fornecedor = st.text_input("URL do Fornecedor (Shopee ou AliExpress)", placeholder="https://...")
        
        # Campo numérico para entrada de preço em Reais (BRL)
        custo_digitado = st.number_input("Custo Bruto no Fornecedor (Em Reais - R\$)", min_value=1.0, value=50.0, step=5.0)
        margem_desejada = st.slider("Margem de Lucro Desejada (%)", min_value=10, max_value=200, value=30, step=5)
        
        btn_cadastrar = st.form_submit_button("Cadastrar e Calcular Margens", use_container_width=True)
        
        if btn_cadastrar and nome_prod and url_fornecedor:
            # Converte BRL para USD para alimentar nativamente o motor fiscal original
            custo_usd = custo_digitado / 5.65
            
            payload = {
                "user_id": st.session_state.user_id,
                "product_name": nome_prod,
                "supplier_url": url_fornecedor,
                "current_cost_usd": round(custo_usd, 2),
                "desired_margin_percent": float(margem_desejada),
                "is_active": True
            }
            try:
                supabase.table("monitored_products").insert(payload).execute()
                st.success(f"🎉 '{nome_prod}' cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

# --- CONTEÚDO PRINCIPAL (PAINEL FISCAL) ---
st.title("📋 Painel de Monitoramento Fiscal")

aba1, aba2 = st.tabs(["📊 Visão Geral do Estoque", "🛒 Checkout Seguro"])

with aba1:
    try:
        query = supabase.table("monitored_products").select("*").eq("user_id", st.session_state.user_id).execute()
        produtos = query.data
        
        if not produtos:
            st.info("💡 Nenhum produto cadastrado na sua conta ainda. Use a barra lateral para adicionar o primeiro!")
        else:
            tabela_dados = []
            for prod in produtos:
                cost_usd = prod.get("current_cost_usd", 3.40)
                url_prod = prod.get("supplier_url", "").lower()
                
                # Regra Inteligente de Origem baseada no input manual
                is_national = ("shopee" in url_prod or ".com.br" in url_prod) and cost_usd < 15.0
                origem = "Nacional 🇧🇷" if is_national else "Internacional 🇨🇳"
                
                # Motor Fiscal Automatizado (Remessa Conforme e ICMS por dentro)
                custo_brl_base = cost_usd * 5.65
                if is_national:
                    custo_com_imposto = custo_brl_base * 1.17  # ICMS padrão nacional
                else:
                    if cost_usd <= 50.0:
                        custo_com_imposto = (custo_brl_base * 1.20) * 1.17  # 20% Importação + 17% ICMS
                    else:
                        custo_com_imposto = (custo_brl_base * 1.60) * 1.17  # 60% Importação + 17% ICMS
                
                margem_fator = 1 + (prod.get("desired_margin_percent", 30.0) / 100.0)
                venda_sugerida = custo_com_imposto * margem_fator
                lucro_liquido = venda_sugerida - custo_com_imposto
                
                tabela_dados.append({
                    "Produto": prod["product_name"],
                    "Origem": origem,
                    "Custo Original (USD)": f"\$ {cost_usd:.2f}",
                    "Custo + Impostos (BRL)": f"R\$ {custo_com_imposto:.2f}",
                    "Venda Sugerida (BRL)": f"R\$ {venda_sugerida:.2f}",
                    "Lucro Líquido": f"R\$ {lucro_liquido:.2f}"
                })
            st.table(tabela_dados)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

with aba2:
    st.subheader("🚀 Escolha o Plano Ideal para sua Operação")
    st.markdown("### 🔥 **14 Dias de Teste Grátis em Qualquer Plano!**")
    st.caption("Experimente a plataforma com todas as funções liberadas. Cancele quando quiser diretamente no painel.")
    st.write("")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("### 📦 Starter\n**R\$ 149** /mês\n* 20 produtos\n* Varredura 12h\n⭐ **14 Dias Grátis**")
        if st.button("Experimentar Starter", key="plan_starter", use_container_width=True):
            st.info("🔄 Iniciando trial do plano Starter via Asaas...")
    with col_p2:
        st.markdown("### ⚡ Pro Scale `Popular`\n**R\$ 299** /mês\n* 100 produtos\n* Varredura 4h\n✅ **Auto-Swap ativo**\n⭐ **14 Dias Grátis**")
        if st.button("Experimentar Pro Scale", key="plan_pro", type="primary", use_container_width=True):
            st.info("🔄 Iniciando trial do plano Pro Scale via Asaas...")
    with col_p3:
        st.markdown("### 👑 Enterprise Premium\n**R\$ 499** /mês\n* 500 produtos\n* Varredura 1h\n✅ **Auto-Swap ativo**\n⭐ **14 Dias Grátis**")
        if st.button("Experimentar Enterprise", key="plan_enterprise", use_container_width=True):
            st.info("🔄 Iniciando trial do plano Enterprise via Asaas...")
