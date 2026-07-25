import logging
import random
import threading
import time
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerencia proxies gratuitos com rotação automática"""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.lock = threading.Lock()
        self.is_updating = False
        self.last_update = 0
        
    def get_free_proxies(self) -> List[str]:
        """Busca proxies gratuitos de várias fontes"""
        proxies = []
        
        # Fonte 1: Free Proxy List
        try:
            url = "https://free-proxy-list.net/"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Pula cabeçalho
                for row in rows[:50]:  # Pega os 50 primeiros
                    cols = row.find_all('td')
                    if len(cols) >= 8:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        https = cols[6].text.strip() == 'yes'
                        if https:
                            proxies.append(f"https://{ip}:{port}")
                        else:
                            proxies.append(f"http://{ip}:{port}")
        except Exception as e:
            logger.warning(f"Erro ao buscar proxies: {e}")
        
        # Fonte 2: ProxyScrape API (grátis)
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                for line in response.text.strip().split('\n'):
                    if ':' in line:
                        ip, port = line.split(':')
                        proxies.append(f"http://{ip}:{port}")
        except Exception as e:
            logger.warning(f"Erro ao buscar proxies do ProxyScrape: {e}")
        
        # Fonte 3: Geonode (grátis)
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for proxy in data.get('data', []):
                    ip = proxy.get('ip')
                    port = proxy.get('port')
                    protocol = proxy.get('protocols', ['http'])[0]
                    if ip and port:
                        proxies.append(f"{protocol}://{ip}:{port}")
        except Exception as e:
            logger.warning(f"Erro ao buscar proxies do Geonode: {e}")
        
        return proxies
    
    def test_proxy(self, proxy: str) -> bool:
        """Testa se o proxy está funcionando"""
        try:
            test_url = "http://httpbin.org/ip"
            proxies = {
                'http': proxy,
                'https': proxy.replace('http://', 'https://')
            }
            response = requests.get(test_url, proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def update_proxy_list(self):
        """Atualiza a lista de proxies em background"""
        if self.is_updating:
            return
        
        self.is_updating = True
        try:
            logger.info("Atualizando lista de proxies...")
            new_proxies = self.get_free_proxies()
            
            # Testa e filtra proxies funcionando
            working_proxies = []
            for proxy in new_proxies[:20]:  # Testa 20 por vez
                if self.test_proxy(proxy):
                    working_proxies.append(proxy)
                    logger.info(f"✅ Proxy funcionando: {proxy}")
            
            with self.lock:
                self.proxies = working_proxies
                self.last_update = time.time()
                
            logger.info(f"✅ {len(self.proxies)} proxies disponíveis")
        except Exception as e:
            logger.error(f"Erro ao atualizar proxies: {e}")
        finally:
            self.is_updating = False
    
    def get_proxy(self) -> Optional[str]:
        """Retorna um proxy aleatório da lista"""
        # Atualiza se lista estiver vazia ou antiga
        if not self.proxies or (time.time() - self.last_update > 300):  # 5 minutos
            self.update_proxy_list()
        
        with self.lock:
            if self.proxies:
                proxy = random.choice(self.proxies)
                self.current_proxy = proxy
                return proxy
        
        return None
    
    def get_headers(self) -> dict:
        """Retorna headers com User-Agent aleatório"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def get_proxy_dict(self) -> dict:
        """Retorna dicionário de proxies para requests"""
        proxy = self.get_proxy()
        if proxy:
            return {
                'http': proxy,
                'https': proxy.replace('http://', 'https://')
            }
        return {}