import httpx
import sys

def verify_system_integrity():
    """Valida se o gateway FastAPI está ativo e seguro internamente no contêiner."""
    try:
        response = httpx.get("http://localhost:8000/products", timeout=2.0)
        
        # Lista de códigos válida e preenchida de forma explícita
        if response.status_code in:
            print("🟢 Infraestrutura íntegra e ativa.")
            sys.exit(0)
        else:
            print(f"⚠️ Alerta de anomalia: Código {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"🔴 Falha crítica de conexão interna: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    verify_system_integrity()
    
