from pydantic.dataclasses import dataclass
from dataclasses import asdict, field
from models.laptop_config_model import LaptopConfigModel
from models.laptop_review_model import LaptopReviewModel


@dataclass
class LaptopModel:
    name: str
    configs: LaptopConfigModel
    base_price: float
    image_url: str
    reviews: LaptopReviewModel
    price_variations: dict[int, float] = field(default_factory=dict)
    
    def set_price_variation(self, hdd: int, price: float):
        """
        Associa um preço a uma variação de HDD.
        
        Argumentos:
            hdd (int): Capacidade do HDD em GB.
            price (float): Preço associado a essa capacidade.
        """
        self.price_variations[hdd] = price

    def to_dict(self) -> dict:
        """
        Converte o objeto para dicionario.
        """
        return asdict(self)

