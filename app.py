import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as chaves de ambiente do arquivo .env local
load_dotenv()

# Inicialização segura do banco de dados na nuvem
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not key:
    key = os.environ.get("SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

st.set_page_config(page_title="DropSync Pulse Pro", page_icon="📡", layout="wide")

# Inicialização inteligente de Estados de Sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "user_id" not in st.session_state:
    try:
        res_perfil = supabase.table("profiles").select("id").limit(1).execute()
        if res_perfil.data:
            st.session_state.user_id = res_perfil.data[0]["id"]
        else:
            st.session_state.user_id = "00000000-0000-0000-0000-000000000000"
    except Exception:
        st.session_state.user_id = "00000000-0000-0000-0000-000000000000"

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown(f"👤 **Logado como:**\n`{st.session_state.user_id[:8]}...`")
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.write("---")
    
    st.subheader("📝 Cadastrar Novo Produto")
    with st.form("form_cadastro", clear_on_submit=True):
        nome_prod = st.text_input("Nome do Produto", placeholder="Ex: Parafusadeira Impacto 48V")
        url_fornecedor = st.text_input("URL do Fornecedor (Shopee ou AliExpress)", placeholder="https://...")
        
        # 🟢 NOVO: Seleção explícita de Origem para evitar erros como o de São Paulo
        tipo_envio = st.selectbox("Origem / Envio do Fornecedor", ["Nacional (Estoque no Brasil 🇧🇷)", "Internacional (Vem da China 🇨🇳)"])
        
        custo_digitado = st.number_input("Custo Bruto no Fornecedor (Em Reais - R\$)", min_value=1.0, value=50.0, step=5.0)
        margem_desejada = st.slider("Margem de Lucro Desejada (%)", min_value=10, max_value=200, value=30, step=5)
        
        btn_cadastrar = st.form_submit_button("Cadastrar e Calcular Margens", use_container_width=True)
        
        if btn_cadastrar:
            if not nome_prod or not url_fornecedor:
                st.warning("⚠️ Preencha todos os campos do formulário!")
            else:
                custo_usd = custo_digitado / 5.65
                
                # Guarda a flag de nacionalidade no payload usando a descrição do fornecedor
                is_nac_flag = True if "Brasil" in tipo_envio else False
                
                payload = {
                    "user_id": st.session_state.user_id,
                    "product_name": nome_prod,
                    "supplier_url": url_fornecedor,
                    "current_cost_usd": round(custo_usd, 2),
                    "desired_margin_percent": float(margem_desejada),
                    "is_active": is_nac_flag # Aproveitamos essa coluna bool do banco temporariamente para guardar a flag de envio
                }
                try:
                    res = supabase.table("monitored_products").insert(payload).execute()
                    if res.data:
                        st.success(f"🎉 '{nome_prod}' cadastrado com sucesso!")
                        st.rerun()
                except Exception as e:
                    st.error(f"🔴 Erro ao salvar: {str(e)}")

# --- CONTEÚDO PRINCIPAL ---
st.title("📋 Painel de Monitoramento Fiscal")

aba1, aba2 = st.tabs(["📊 Visão Geral do Estoque", "🛒 Checkout Seguro"])

with aba1:
    try:
        query = supabase.table("monitored_products").select("*").eq("user_id", st.session_state.user_id).execute()
        produtos = query.data
        
        if not produtos:
            st.info("💡 Nenhum produto cadastrado na sua conta ainda.")
        else:
            tabela_dados = []
            for prod in produtos:
                cost_usd = prod.get("current_cost_usd", 3.40)
                
                # Lê a flag salva diretamente do cadastro
                is_national = prod.get("is_active", True)
                origem = "Nacional 🇧🇷" if is_national else "Internacional 🇨🇳"
                
                custo_brl_base = cost_usd * 5.65
                
                # Executa o cálculo tributário exato com base na origem real escolhida
                if is_national:
                    custo_com_imposto = custo_brl_base * 1.17  # Apenas ICMS por dentro brasileiro de SP
                else:
                    if cost_usd <= 50.0:
                        custo_com_imposto = (custo_brl_base * 1.20) * 1.17  # Remessa Conforme Abaixo de \$50
                    else:
                        custo_com_imposto = (custo_brl_base * 1.60) * 1.17  # Remessa Conforme Acima de \$50
                
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
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("### 📦 Starter\n**R\$ 149** /mês\n⭐ **14 Dias Grátis**")
    with col_p2:
        st.markdown("### ⚡ Pro Scale `Popular`\n**R\$ 299** /mês\n* 100 produtos\n* Varredura 4h\n✅ **Auto-Swap ativo**\n⭐ **14 Dias Grátis**")
        # 🟢 Cole o link final copiado do Asaas aqui dentro das aspas:
        st.link_button("Experimentar Pro Scale", "Cttps://www.asaas.com/000/c/188cedhmngads35s", type="primary", use_container_width=True)
    with col_p3:
        st.markdown("### 👑 Enterprise Premium\n**R\$ 499** /mês\n⭐ **14 Dias Grátis**")
