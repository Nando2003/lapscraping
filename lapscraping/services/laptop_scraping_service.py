from external.laptop_store import LaptopStore
from models import (LaptopConfigModel,
                    LaptopModel, 
                    LaptopReviewModel)
from config.settings import Settings
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import re


class LaptopScrapingService:
    
    def __init__(self):
        self.laptop_store = LaptopStore()
        
    def get_laptops(self):
        laptops: list[LaptopModel] = []
        
        main_content = self.laptop_store.get_page_content()
        soup = BeautifulSoup(main_content, "html.parser")
        
        hdd_prices = self._get_hdd_prices(soup)
        hrefs = self._get_href_from_laptops_cards(soup)
        max_page = self._get_last_page(soup)
        
        for href in hrefs:
            laptop_content = self.laptop_store.get_page_content(href)
            laptop_soup = BeautifulSoup(laptop_content, "html.parser")
            laptops.append(self._get_laptop(laptop_soup, hdd_prices))
            
        for page in range(2, max_page + 1):
            other_content = self.laptop_store.get_page_content(f"?page={page}")
            soup = BeautifulSoup(other_content, "html.parser")
            hrefs = self._get_href_from_laptops_cards(soup)
            
            for href in hrefs:
                laptop_content = self.laptop_store.get_page_content(href)
                laptop_soup = BeautifulSoup(laptop_content, "html.parser")
                laptops.append(self._get_laptop(laptop_soup, hdd_prices))

        return laptops
        
    def _get_laptop(self, soup: BeautifulSoup, hdd_prices: dict[int, float]) -> LaptopModel:
        product_wrapper = soup.select_one("div.product-wrapper.card-body")
        
        if product_wrapper:
            
            laptop_name_tag = product_wrapper.select_one('h4.title.card-title')
            image_tag = product_wrapper.select_one('img.image.img-fluid.img-responsive')
            price_tag = product_wrapper.select_one('h4.price.float-end.pull-right')
            
            if not (laptop_name_tag and image_tag and price_tag):
                raise ValueError("Nome do produto, imagem ou preço não encontrados")
            
            image_tag = product_wrapper.select_one('img.image.img-fluid.img-responsive')
            price_tag = product_wrapper.select_one('h4.price.float-end.pull-right')
            
            if not (image_tag and price_tag):
                raise ValueError("Imagem, preço não encontrados")
            
            image_src = image_tag.get("src")
            
            if not image_src:
                raise ValueError("Imagem não encontrada")
            
            price_text = price_tag.text.strip()
            price_group = re.search(r'([\d.,]+)', price_text)
            
            if not price_group:
                raise ValueError("Preço não encontrado")
            
            price = float(price_group.group(1))
            
            swatch_buttons = product_wrapper.select("div.swatches button")
            
            available_hdds = [
                int(button["value"]) # type: ignore
                for button in swatch_buttons 
                if not button.has_attr("disabled")
            ]
            
            laptop_model = LaptopModel(
                name=laptop_name_tag.text.strip(),
                configs=self._get_laptop_config(product_wrapper),
                base_price=price,
                image_url=urljoin(Settings.LAPTOP_BASE_URL, str(image_src)),
                reviews=self._get_laptop_reviews(product_wrapper)
            )
            
            for hdd in available_hdds:
                
                if hdd in hdd_prices:
                    price += hdd_prices[hdd]
                    
                laptop_model.set_price_variation(hdd, price)
        
        else:
            raise ValueError("Product wrapper não encontrado")
        
        return laptop_model
    
    def _get_laptop_config(self, soup: Tag) -> LaptopConfigModel:
        configs_tag = soup.select_one("p.description.card-text")
            
        if not configs_tag:
            raise ValueError("Configuração não encontrada")
        
        configs = configs_tag.text.strip()
        
        parts = [
            part for part in [p.strip() for p in re.split(r',|\.\s+', configs)]
        ]
        
        screen_spec = None
        keyboard_layout = None
        graphics_card = None
        osys = None
        cpu = None
        ram = None
        hdd = None
        
        can_be_graphics_card = True
        
        for idx, part in enumerate(parts):
            
            if '"' in part: # Pega tudo do primeiro numero ate o final
                screen_spec_match = re.search(r'(\d{1,2}(?:\.\d{1,2})?".*)', part)
                screen_spec = screen_spec_match.group(1) if screen_spec_match else None
                continue
            
            if not ram:
                
                if "gb" in part.lower():
                    ram = part 
                    cpu = parts[idx - 1] # Se encontrar a ram o anterior é o cpu    
                    continue
            
            else:
                    
                if not hdd:
                    hdd = part # Se entrou a ram, o proximo eh o hdd
                    continue
                
                else:
                    
                    if not osys:
                        # Verifica se o sistema operacional esta na lista de palavras-chaves
                        for os_part in Settings.OS_KEYWORDS:
                                
                            if os_part in part.lower():
                                osys = part
                                can_be_graphics_card = False
                                break # Quando encontrar o sistema operacional, sai do loop
                            
                        if osys: 
                            continue # Se ja tiver um sistema operacional, não precisa continuar 
                    
                    # Se osys foi preenchido entao nao pode ser placa de video
                    if not graphics_card and can_be_graphics_card: 
                            
                            if len(part) < 4: # Se for menor que 4, 
                                continue # não é uma placa de video
                            
                            graphics_card = part
                            continue
                        
                    if osys: # Se ja tiver um sistema operacional 
                        keyboard_layout = part # então o próximo é o teclado
                        continue
            
        if not (cpu and ram and hdd):
            raise ValueError("Configuração incompleta")
            
        return LaptopConfigModel(
            screen_spec=screen_spec,
            cpu=cpu,
            ram=ram,
            hdd=hdd,
            os=osys,
            graphics_card=graphics_card,
            keyboard_layout=keyboard_layout
        )
    
    def _get_laptop_reviews(self, soup: Tag) -> LaptopReviewModel: 
        reviews_tag = soup.select_one("p.review-count")
            
        if not reviews_tag:
            raise ValueError("Reviews não encontradas")
        
        reviews = reviews_tag.text.strip()
        reviews_group = re.search(r'(\d+)', reviews)
        amount_of_reviews = int(reviews_group.group(1)) if reviews_group else 0
        stars = reviews_tag.select("span.ws-icon.ws-icon-star")
        
        return LaptopReviewModel(
            stars=len(stars),
            amont_of_reviews=amount_of_reviews
        )
        
    def _get_hdd_prices(self, soup: BeautifulSoup) -> dict[int, float]:
        script_tag = soup.find("script", src=lambda x: x and "app.js" in x) # type: ignore
        
        if not script_tag:
            raise ValueError("Script não encontrado")
            
        script_src = script_tag.get("src") # type: ignore
            
        if not script_src:
            raise ValueError("Script src não encontrado")

        script_content = self.laptop_store.get_page_content(str(script_src))
        pattern = r'case"(\d+)":n=(\d+);?'
        matches = re.findall(pattern, script_content)

        return {
            int(hdd): float(adicional) 
            for hdd, adicional in matches
        }
        
    def _get_href_from_laptops_cards(self, soup: BeautifulSoup) -> list[str]:
        product_cards = soup.select("div.col-md-4.col-xl-4.col-lg-4")
        hrefs: list[str] = []
        
        for card in product_cards:
            caption = card.select_one("div.caption")
            
            if not caption:
                continue
            
            title_tag = caption.select_one("h4 > a[href]")
            
            if not title_tag:
                continue
            
            href = title_tag.get("href")
            
            if not href:
                continue
            
            hrefs.append(str(href))
            
        return hrefs  
        
    def _get_last_page(self, soup: BeautifulSoup) -> int:
        page_links = soup.select("a.page-link")
        
        numeric_pages = [
            link for link in page_links 
            if link.text.strip().isdigit()
        ]
        
        if not numeric_pages:
            raise ValueError("Página maxima não encontrada")
        
        return int(numeric_pages[-1].text.strip())
    