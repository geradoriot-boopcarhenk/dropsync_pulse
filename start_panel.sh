#!/bin/bash
# =========================================================================
# DropSync Pulse - Script de Inicialização Unificado e Automatizado
# =========================================================================

PROJECT_DIR="$HOME/dropsync_pulse"
cd "$PROJECT_DIR" || { echo "❌ Erro: Diretório não encontrado."; exit 1; }

echo "========================================================"
echo "⚡ Iniciando Ecossistema Integrado DropSync Pulse..."
echo "========================================================"

# 1. Inicializa o Gateway API Central (FastAPI) na porta 8000
echo "🌐 Ligando API Gateway (FastAPI / Uvicorn)..."
uvicorn main:app --port 8000 --log-level warning &
FASTAPI_PID=$!

# 2. Inicializa o painel visual do Streamlit
echo "🚀 Ligando Painel Administrativo (Streamlit)..."
streamlit run app.py --server.headless=false &
STREAMLIT_PID=$!

echo "⏱️ Aguardando inicialização dos servidores..."
sleep 3

echo "========================================================"
echo "📡 Iniciando Worker do Robô e Exibindo Logs Locais..."
echo "Pressione [Ctrl + C] para encerrar todo o ecossistema."
echo "========================================================"

# Função para matar os servidores em background de forma limpa ao sair
comportamento_saida() {
    echo -e "\n🛑 Derrubando servidores locais..."
    kill $FASTAPI_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo "💡 Ecossistema encerrado com sucesso."
    exit 0
}

# Intercepta o sinal de encerramento Ctrl+C
trap comportamento_saida INT

# 3. Mantém a tela presa exibindo o loop do robô de raspagem de preços
python worker.py
