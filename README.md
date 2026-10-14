# ⚡ DropSync Pulse

Sistema SaaS corporativo em Python projetado para monitoramento fiscal, inteligência de estoque em tempo real e contingência automática (Auto-Swap) para lojistas de Dropshipping (AliExpress e Shopee).

---

## 🚀 Arquitetura do Sistema e Módulos

O ecossistema é modularizado em microsserviços integrados de alta performance:

*   **`main.py` (FastAPI)**: API Gateway central responsável pelo roteamento, validação e recepção assíncrona de Webhooks do Asaas.
*   **`app.py` (Streamlit)**: Dashboard visual do lojista, contendo análise fiscal de margem e esteira de checkout.
*   **`worker.py` & `scraper.py`**: Robô assíncrono controlado por concorrência via Semáforos (`asyncio`), executando raspagens via proxies residenciais e disparando o **Auto-Swap inteligente** caso um produto esgote na fonte.
*   **`integrator.py` & `payment.py`**: Motor fiscal adaptado às regras do *Remessa Conforme* (ICMS por dentro) e faturamento via Pix com o Asaas.
*   **`alerts.py`**: Mensageria integrada combinando disparos via Telegram Bot e Push Notifications através do **Firebase Admin SDK**.
*   **`logs.py` & `stress_test.py`**: Auditoria física rotativa em arquivos e script de simulação de carga massiva concorrente.
*   **`seed.py`**: Script de semente para migração automatizada e população inicial de tabelas do Supabase.

---

## 🛠️ Como Rodar o Projeto do Zero

### 1. Requisitos Prévios (Instalação no Fedora)
```bash
sudo dnf install python3-pip -y
pip install supabase httpx firebase-admin python-dotenv BeautifulSoup4 streamlit pandas fastapi uvicorn reportlab
```

### 2. Configuração de Variáveis (`.env`)
Crie um arquivo `.env` na raiz do projeto com o padrão:
```ini
SUPABASE_URL=https://supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua-chave-administrativa
ASAAS_API_URL=https://asaas.com
ASAAS_API_KEY=$aact_prod_...
ASAAS_WEBHOOK_TOKEN=seu_token_secreto
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id
```

### 3. Semente do Banco de Dados
Antes da primeira execução, popule as tabelas do seu Supabase:
```bash
python seed.py
```

### 4. Inicialização Unificada
Para subir a API, o Painel Visual e o Robô de uma única vez com logs ativos no terminal do seu Fedora, basta rodar:
```bash
chmod +x start_panel.sh
./start_panel.sh
```
O painel estará disponível em `http://localhost:8501`.
