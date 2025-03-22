from typing import Optional, Literal
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from services.laptop_scraping_service import LaptopScrapingService
from models.laptop_model import LaptopModel

router = APIRouter()
service = LaptopScrapingService()

SortOptions = Literal["price", "name", "ram", "hdd", "reviews", "stars"]


@router.get("/laptops", response_model=list[LaptopModel],)
def get_laptops(
    sort_by: Optional[SortOptions] = Query(default=None),
    reverse: Optional[bool] = Query(default=None),
    search_by_name: Optional[str] = Query(default=None)
):
    """
    Rota para obter laptops da loja, com ordenação e filtro por nome.

    Parâmetros:
    - sort_by: 'price', 'name', 'ram', 'hdd', 'reviews', 'stars'
    - reverse: inverte a ordenação
    - search_by_name: filtra por parte do nome (case-insensitive)
    """
    try:
        laptops = service.get_laptops(search_by_name)
        
        try:
            if sort_by:
                
                if sort_by == "price":
                    laptops.sort(key=lambda laptop: laptop.base_price)
                    
                elif sort_by == "name":
                    laptops.sort(key=lambda laptop: laptop.name.lower())
                    
                elif sort_by == "ram":
                    laptops.sort(key=lambda laptop: int(laptop.configs.ram.replace("GB", "").strip()))
                    
                elif sort_by == "hdd":
                    laptops.sort(key=lambda laptop: int(laptop.configs.hdd.replace("GB", "").replace("TB", "000").strip()))
                    
                elif sort_by == "reviews":
                    laptops.sort(key=lambda laptop: laptop.reviews.amont_of_reviews, reverse=True)
                    
                elif sort_by == "stars":
                    laptops.sort(key=lambda laptop: laptop.reviews.stars, reverse=True)
                
                if isinstance(reverse, bool) and reverse:
                    laptops.reverse()
            
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Erro ao ordenar por '{sort_by}': {str(e)}"})
        
        return [LaptopModel(**laptop.to_dict()) for laptop in laptops]
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erro ao obter laptops: {str(e)}"})
    