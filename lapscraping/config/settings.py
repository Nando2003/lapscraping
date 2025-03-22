import os


class Settings:
    # URL base do site para scraping
    LAPTOP_BASE_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"
    
    # Headers para requisições
    DEFAULT_HEADERS = {
        "accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Opera GX";v="117"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ),
    }
    
    OS_KEYWORDS = ["win", "64bit", "32bit", "windows", "linux", "macos", "os"] 
    
    # Passe os proxys caso tenha
    PROXIES_LIST = os.getenv("PROXIES_LIST", "").split(",") if os.getenv("PROXIES_LIST") else []