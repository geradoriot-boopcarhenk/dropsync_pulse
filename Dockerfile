FROM python:3.11-slim

WORKDIR /app

# Instala o Supervisor de forma nativa via gerenciador de pacotes do Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copia a receita do gerenciador para a pasta de configuração padrão
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
EXPOSE 8501

# Altera o ponto de entrada do contêiner para o Supervisor controlar a sessão
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
