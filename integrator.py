import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from integrator import calculate_brazilian_taxes
from export_report import generate_pdf_report

load_dotenv()

st.set_page_config(page_title="DropSync Pulse", page_icon="⚡", layout="wide")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if "user_id" not in st.session_state:
    st.session_state["user_id"] = "00000000-0000-0000-0000-000000000000"

st.title("⚡ DropSync Pulse — Dashboard Analítico")
st.caption("Monitoramento fiscal, estoque e contingência em tempo real para Dropshipping")

aba1, aba2 = st.tabs(["📊 Painel Analítico Geral", "🛒 Checkout Seguro"])

with aba1:
    # --- BARRA LATERAL ---
    st.sidebar.header("📦 Novo Produto")
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
                    "current_cost_usd": 10.00
                }
                supabase.table("monitored_products").insert(payload).execute()
                st.sidebar.success("Produto adicionado à fila do Scraper!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Erro: {str(e)}")

    # --- MÉTRICAS GERAIS ---
    try:
        prod_query = supabase.table("monitored_products").select("*").execute()
        df_products = pd.DataFrame(prod_query.data)

        if not df_products.empty:
            swap_query = supabase.table("supplier_swaps").select("*").execute()
            df_swaps = pd.DataFrame(swap_query.data)
            total_swaps = len(df_swaps) if not df_swaps.empty else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Produtos Monitorados", len(df_products))
            col2.metric("Scrapers Ativos", len(df_products[df_products["is_active"] == True]))
            col3.metric("Auto-Swaps Executados", total_swaps)
            col4.metric("Status da API", "Online 🚀")

            st.subheader("📋 Painel de Monitoramento Fiscal")
            rows = []
            raw_products_list = []
            
            df_actives = df_products[df_products["is_active"] == True]

            if not df_actives.empty:
                for _, row in df_actives.iterrows():
                    cost_usd = row.get("current_cost_usd")
                    margin_percent = row.get("desired_margin_percent")
                    
                    cost_usd = float(cost_usd) if cost_usd is not None else 10.00
                    margin_percent = float(margin_percent) if margin_percent is not None else 30.0
                    
                    try:
                        # Processa individualmente com proteção contra falhas locais
                        fiscal = calculate_brazilian_taxes(cost_usd, margin_percent)
                        
                        raw_products_list.append({
                            "id": row["id"],
                            "product_name": row["product_name"],
                            "current_cost_usd": cost_usd,
                            "desired_margin_percent": margin_percent,
                            "is_active": row["is_active"]
                        })
                        
                        rows.append({
                            "ID": row["id"],
                            "Produto": row["product_name"],
                            "Custo Original (USD)": f"$ {cost_usd:.2f}",
                            "Custo + Impostos (BRL)": f"R$ {fiscal['custo_nacionalizado_total']:.2f}",
                            "Venda Sugerida (BRL)": f"R$ {fiscal['preco_venda_final_loja']:.2f}",
                            "Lucro Líquido (BRL)": f"R$ {fiscal['lucro_liquido_venda']:.2f}",
                            "Status": "Ativo 🟢"
                        })
                    except Exception as cell_err:
                        continue
                
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                    
                    # --- SEÇÃO DE EXPORTAÇÃO CORPORATIVA ---
                    st.markdown("---")
                    st.subheader("📥 Exportação de Dados")
                    
                    try:
                        pdf_path = generate_pdf_report(raw_products_list)
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📄 Baixar Relatório de Auditoria Fiscal (PDF)",
                                data=f,
                                file_name="auditoria_dropsync_pulse.pdf",
                                mime="application/pdf"
                            )
                    except Exception as pdf_err:
                        st.error(f"Erro ao preparar o arquivo PDF: {str(pdf_err)}")
                else:
                    st.info("Aguardando o robô de raspagem processar dados válidos.")
            else:
                st.info("Nenhum produto marcado como ativo ('is_active = true') no momento.")
        else:
            st.info("Nenhum produto cadastrado no banco de dados.")
    except Exception as e:
        st.error(f"Erro crítico na renderização da interface: {str(e)}")

with aba2:
    st.subheader("🛒 Simulador de Checkout")
