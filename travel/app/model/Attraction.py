from typing import Optional

from pydantic import BaseModel, Field

from app.model.Location import Location


class Attraction(BaseModel):
    name: str = Field(..., description='Attraction name')
    address: str = Field(..., description='Attraction address')
    location: Location = Field(..., description='Attraction location(longitude and latitude)')
    visit_duration: int = Field(..., description='recommend visit duration in minutes', gt=0)
    description: str = Field(..., description='Attraction description')
    category: Optional[str] = Field(..., description='Attraction category')
    rating: Optional[float] = Field(default=None, description='Attraction rating', ge=0, le=5)
    image_url: Optional[str] = Field(default=None, description='Attraction image url')
    ticket_price: int = Field(default=0, description='Attraction ticket price(rmb)', ge=0)
