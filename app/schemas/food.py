from pydantic import BaseModel
from typing import Optional

class FoodCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None
