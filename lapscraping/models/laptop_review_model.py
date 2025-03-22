from pydantic.dataclasses import dataclass


@dataclass
class LaptopReviewModel:
    stars: int
    amont_of_reviews: int    