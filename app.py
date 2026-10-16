import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from integrator import calculate_brazilian_taxes
from export_report import generate_pdf_report

load_dotenv()

st.set_page_config(page_title="DropSync Pulse Pro", page_icon="⚡", layout="wide")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GERENCIAMENTO DE SESSÃO E AUTH ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.session_state["user_email"] = ""

# --- TELA DE LOGIN / CADASTRO COMERCIAL ---
if not st.session_state["authenticated"]:
    st.title("⚡ DropSync Pulse — Login")
    st.caption("Acesse sua infraestrutura de monitoramento e contingência de Dropshipping")
    
    aba_login, aba_cadastro = st.tabs(["🔒 Entrar na Conta", "📝 Criar Conta SaaS"])
    
    with aba_login:
        email = st.text_input("E-mail corporativo", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Autenticar", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = res.user.id
                st.session_state["user_email"] = res.user.email
                st.success("Autenticado com sucesso! Carregando infraestrutura...")
                st.rerun()
            except Exception as e:
                st.error("Credenciais inválidas ou conta não confirmada.")
                
    with aba_cadastro:
        new_email = st.text_input("Melhor E-mail", key="cad_email")
        new_senha = st.text_input("Defina uma Senha Segura", type="password", key="cad_senha")
        if st.button("Registrar Minha Loja"):
            try:
                res = supabase.auth.sign_up({"email": new_email, "password": new_senha})
                perfil_payload = {
                    "id": res.user.id,
                    "store_url": "https://nova-loja-configurar.com",
                    "plan_id": 2,
                    "subscription_status": "trial"
                }
                supabase.table("profiles").insert(perfil_payload).execute()
                st.success("Conta criada! Verifique seu e-mail para confirmar o cadastro.")
            except Exception as e:
                st.error(f"Erro ao registrar: {str(e)}")
    st.stop()

# --- VALIDAR STATUS DE ASSINATURA ---
try:
    profile_query = supabase.table("profiles").select("subscription_status").eq("id", st.session_state["user_id"]).execute()
    sub_status = profile_query.data[0].get("subscription_status", "trial") if profile_query.data else "canceled"
except Exception:
    sub_status = "canceled"

if sub_status in ["overdue", "canceled"]:
    st.error("🚨 CONTA BLOQUEADA OU INADIMPLENTE")
    st.subheader("Verificamos uma pendência na sua assinatura do DropSync Pulse.")
    st.write("Para regularizar sua situação e reativar seus scrapers, atualize sua conta no menu financeiro.")
    st.stop()

# --- PAINEL PRINCIPAL RENDERIZADO APENAS PARA CLIENTES ATIVOS ---
st.title("⚡ DropSync Pulse — Dashboard Analítico")
st.sidebar.markdown(f"👤 **Logado como:**\n`{st.session_state['user_email']}`")
if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state["authenticated"] = False
    st.session_state["user_id"] = None
    st.rerun()

aba1, aba2 = st.tabs(["📊 Painel Analítico Geral", "🛒 Checkout Seguro"])

with aba1:
    # --- BARRA LATERAL MULTI-TENANT ---
    st.sidebar.header("📦 Adicionar Link")
    prod_name = st.sidebar.text_input("Nome do Produto")
    supplier_url = st.sidebar.text_input("Link do Fornecedor")
    margin = st.sidebar.slider("Margem de Lucro Desejada (%)", 10, 200, 30)

    if st.sidebar.button("Ativar Monitoramento", type="primary"):
        if prod_name and supplier_url:
            try:
                payload = {
                    "user_id": st.session_state["user_id"],
                    "product_name": prod_name,
                    "supplier_url": supplier_url,
                    "desired_margin_percent": float(margin),
                    "current_cost_usd": 3.40  # Inicia com valor padrão ajustado de mercado
                }
                supabase.table("monitored_products").insert(payload).execute()
                st.sidebar.success("Produto adicionado à sua fila!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Erro: {str(e)}")

    # --- LISTAGEM ISOLADA POR USUÁRIO ---
    try:
        prod_query = supabase.table("monitored_products").select("*").eq("user_id", st.session_state["user_id"]).execute()
        df_products = pd.DataFrame(prod_query.data)

        if not df_products.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Seus Produtos", len(df_products))
            col2.metric("Scrapers Ativos", len(df_products[df_products["is_active"] == True]))
            col3.metric("Status da Assinatura", sub_status.upper())

            st.subheader("📋 Painel de Monitoramento Fiscal")
            rows = []
            raw_products_list = []
            
            df_actives = df_products[df_products["is_active"] == True]

            if not df_actives.empty:
                for _, row in df_actives.iterrows():
                    cost_usd = row.get("current_cost_usd")
                    margin_percent = row.get("desired_margin_percent")
                    url_fornecedor = row.get("supplier_url", "").lower()
                    
                    cost_usd = float(cost_usd) if cost_usd is not None else 10.00
                    margin_percent = float(margin_percent) if margin_percent is not None else 30.0
                    
                    # Identificacao Inteligente: chaveia para nacional se o link possuir marcas locais (.br) ou custo reduzido
                                        # Ajuste Cirúrgico: Só considera nacional se o link contiver explicitamente shopee ou .com.br
                    # Links do AliExpress (.com) ou com custo internacional passam obrigatoriamente pela esteira aduaneira
                    is_national = ("shopee" in url_fornecedor or ".com.br" in url_fornecedor) and "aliexpress" not in url_fornecedor

                    
                    try:
                        fiscal = calculate_brazilian_taxes(cost_usd, margin_percent, is_national=is_national)
                        raw_products_list.append({
                            "id": row["id"], "product_name": row["product_name"],
                            "current_cost_usd": cost_usd, "desired_margin_percent": margin_percent,
                            "is_active": row["is_active"]
                        })
                        rows.append({
                            "ID": row["id"], "Produto": row["product_name"],
                            "Origem": "Nacional 🇧🇷" if is_national else "Internacional 🇨🇳",
                            "Custo Original (USD)": f"\$ {cost_usd:.2f}",
                            "Custo + Impostos (BRL)": f"R\$ {fiscal['custo_nacionalizado_total']:.2f}",
                            "Venda Sugerida (BRL)": f"R\$ {fiscal['preco_venda_final_loja']:.2f}",
                            "Lucro Líquido (BRL)": f"R\$ {fiscal['lucro_liquido_venda']:.2f}"
                        })
                    except Exception:
                        continue
                
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                    st.markdown("---")
                    pdf_path = generate_pdf_report(raw_products_list)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 Baixar Relatório de Auditoria Fiscal (PDF)",
                            data=f, file_name="auditoria_dropsync_pulse.pdf", mime="application/pdf"
                        )
                else:
                    st.info("Aguardando os scrapers processarem dados válidos.")
            else:
                st.info("Nenhum produto ativado na sua conta no momento.")
        else:
            st.info("Sua esteira de monitoramento está vazia. Adicione o seu primeiro produto na barra lateral!")
    except Exception as e:
        st.error(f"Erro na camada visual: {str(e)}")

with aba2:
    st.subheader("🛒 Planos e Licenciamento Ativo")
