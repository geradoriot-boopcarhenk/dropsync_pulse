import os
import re
import json
import httpx
from bs4 import BeautifulSoup

class EnterpriseMarketScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://shopee.com.br"
        }
        self.proxy_user = os.environ.get("PROXY_USER")
        self.proxy_pass = os.environ.get("PROXY_PASS")
        self.proxy_host = os.environ.get("PROXY_HOST")

    def _get_proxy_configuration(self) -> dict:
        if not self.proxy_user or self.proxy_user == "seu_usuario_proxy":
            return {}
        proxy_url = f"http://{self.proxy_user}:{self.proxy_pass}@{self.proxy_host}"
        return {"http://": proxy_url, "https://": proxy_url}

    def _extract_shopee_ids(self, url: str) -> tuple:
        match = re.search(r'i\.(\d+)\.(\d+)', url)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _fetch_shopee(self, url: str) -> dict:
        shop_id, item_id = self._extract_shopee_ids(url)
        if not shop_id or not item_id:
            return {"error": "URL da Shopee fora do padrao"}
        
        api_url = f"https://shopee.com.br{item_id}&shopid={shop_id}"
        try:
            with httpx.Client(proxies=self._get_proxy_configuration(), headers=self.headers, timeout=12.0) as client:
                response = client.get(api_url)
                if response.status_code == 200:
                    item = response.json().get("data", {})
                    if not item:
                        return {"error": "Produto indisponivel"}
                    raw_price = item.get("price") or item.get("price_min")
                    price_brl = float(raw_price) / 100000.0 if raw_price else 0.0
                    return {"price_usd": round(price_brl / 5.65, 2), "in_stock": item.get("stock", 0) > 0}
        except Exception as e:
            return {"error": str(e)}
        return {"error": "Erro desconhecido"}

    def _fetch_aliexpress(self, url: str) -> dict:
        try:
            with httpx.Client(proxies=self._get_proxy_configuration(), headers=self.headers, timeout=15.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    script_tag = soup.find('script', type='application/ld+json')
                    if script_tag:
                        product_data = json.loads(script_tag.string)
                        offers = product_data.get("offers", {})
                        price = offers.get("price") or offers.get("lowPrice")
                        currency = offers.get("priceCurrency", "USD")
                        price_usd = float(price) / 5.65 if currency == "BRL" else float(price)
                        return {"price_usd": round(price_usd, 2), "in_stock": "InStock" in offers.get("availability", "")}
        except Exception as e:
            return {"error": str(e)}
        return {"error": "Estrutura nao encontrada"}

    def find_alternative_supplier_aliexpress(self, product_name: str) -> str:
        """MÓDULO AUTO-SWAP: Busca um fornecedor substituto no AliExpress baseado no título."""
        search_query = product_name.replace(" ", "+")
        search_url = f"https://aliexpress.com{search_query}.html"
        print(f"🔄 [Auto-Swap] Buscando alternativa para '{product_name}' no AliExpress...")
        try:
            with httpx.Client(proxies=self._get_proxy_configuration(), headers=self.headers, timeout=10.0) as client:
                response = client.get(search_url)
                if response.status_code == 200:
                    # Filtra e extrai a primeira URL de produto válida encontrada na listagem de busca
                    urls_encontradas = re.findall(r'href="//www\.aliexpress\.com/item/(\d+)\.html"', response.text)
                    if urls_encontradas:
                        link_substituto = f"https://aliexpress.com{urls_encontradas[0]}.html"
                        print(f"✅ [Auto-Swap] Novo fornecedor encontrado: {link_substituto}")
                        return link_substituto
        except Exception as e:
            print(f"❌ [Auto-Swap] Falha na busca de contingência: {str(e)}")
        return None

    def fetch_product_data(self, url: str) -> dict:
        if "shopee.com" in url:
            return self._fetch_shopee(url)
        elif "aliexpress.com" in url:
            return self._fetch_aliexpress(url)
        return {"error": "Fornecedor nao suportado"}
