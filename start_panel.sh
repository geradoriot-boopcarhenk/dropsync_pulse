#!/bin/bash
# =========================================================================
# DropSync Pulse - Script de Produção para Contêiner Docker (Nuvem)
# =========================================================================

echo "========================================================"
echo "⚡ Inicializando Servidores DropSync Pulse na Nuvem..."
echo "========================================================"

# 1. Inicializa o Gateway API (FastAPI) em segundo plano
echo "🌐 Ligando API Gateway (FastAPI)..."
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning &

# 2. Inicializa o Robô de Variação de Preço (Worker) em segundo plano
echo "📡 Ligando Robo de Monitoramento Assincrono..."
python worker.py &

# 3. Inicializa o Streamlit EM PRIMEIRO PLANO (TRAVANDO O CONTÊINER ATIVO)
# Nota: O Railway usa uma variável interna chamada PORT. Vamos escutar nela.
echo "🚀 Ligando Painel Administrativo Visual (Streamlit)..."
streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless=true
