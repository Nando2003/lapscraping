import requests
from tenacity import (retry, 
                      wait_exponential,
                      stop_after_attempt,
                      retry_if_exception_type)
from typing import Optional
from urllib.parse import urljoin
from config.settings import Settings


class LaptopStore:
    
    CYCLE_LENGTH: int
    request_counter: int
    
    def __init__(self):
        self.CYCLE_LENGTH = 2 + (len(Settings.PROXIES_LIST) * 2)
        self.request_counter = 0
        
        self.session = requests.Session()
        self.session.headers.update(Settings.DEFAULT_HEADERS)
    
    @retry(
        stop=stop_after_attempt(5), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def get_page_content(self, href_url: Optional[str] = None, **kwargs) -> str:
        """
        Pega o conteúdo da página da loja de laptops.
        
        Argumentos:
            href_url (str): URL relativa da página a ser acessada.
        
        Retorna:
            str: Conteúdo da página.
        """
        
        base_url = (
            Settings.LAPTOP_BASE_URL
            if not href_url 
            else urljoin(Settings.LAPTOP_BASE_URL, href_url)
        )
        
        cycle_position = self.request_counter % self.CYCLE_LENGTH
        self.request_counter += 1 # Incrementa o contador
        
        # Default: sem proxy
        proxies_used = None

        if Settings.PROXIES_LIST and cycle_position >= 2:
            proxy_index = (cycle_position - 2) // 2
            
            # VERIFICACAO EXTRA
            if proxy_index < len(Settings.PROXIES_LIST):
                proxy = Settings.PROXIES_LIST[proxy_index]
                proxies_used = {
                    "http": proxy,
                    "https": proxy,
                }

        response = self.session.get(url=base_url, 
                                    proxies=proxies_used, 
                                    timeout=10, 
                                    **kwargs)
        
        response.raise_for_status()
        return response.text