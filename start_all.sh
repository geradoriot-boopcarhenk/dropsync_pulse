#!/bin/bash
# Script de Inicialização Completa do DropSync Pulse

cd ~/dropsync_pulse

# Ativa o ambiente virtual
source .venv/bin/activate

echo "⚡ Iniciando ecossistema DropSync Pulse em Background..."

# 1. Inicia o Túnel do ngrok
nohup ngrok http 8000 > ngrok.log 2>&1 &
echo "🌐 ngrok ativado."

# 2. Inicia o FastAPI/Uvicorn (Faturamento)
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
echo "💳 FastAPI ativado."

# 3. Inicia o Worker (Rastreador Shopee e Telegram)
nohup python -B worker.py > worker.log 2>&1 &
echo "🤖 Worker de Varredura ativado."

# 4. Inicia o Painel Visual Streamlit
nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
echo "📊 Painel Streamlit ativado."

echo "🚀 Todos os motores estão rodando perfeitamente!"
