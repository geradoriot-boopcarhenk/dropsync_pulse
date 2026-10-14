import os
import logging
from logging.handlers import RotatingFileHandler

# Cria a pasta de logs se ela não existir no sistema
LOG_DIR = os.path.expanduser("~/dropsync_pulse/logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "dropsync.log")

# Configura o Logger com rotação automática (Gera arquivos novos se passar de 5MB)
logger = logging.getLogger("DropSyncPulse")
logger.setLevel(logging.INFO)

# Impede a criação de múltiplos handlers duplicados
if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Rotação de arquivos: Mantém até 3 arquivos de backup de 5MB cada
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    # Exibição paralela limpa no terminal do Fedora
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_info(message: str):
    logger.info(message)

def log_warning(message: str):
    logger.warning(message)

def log_error(message: str):
    logger.error(message)
