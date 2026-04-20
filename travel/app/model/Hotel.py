from typing import Optional

from pydantic import BaseModel, Field

from app.model.Location import Location


class Hotel(BaseModel):
    '''information of a hotel'''
    name: str = Field(..., description='Hotel Name')
    address: str = Field(description='Hotel Address')
    location: Optional[Location] = Field(default=None, description='Location of meal')
    price_range: str = Field(..., description='Price range of hotel')
    rating: Optional[float] = Field(default=None, description='Hotel rating', ge=0, le=5)
    distance: str = Field(..., description='Hotel distance from the attraction')
    cost: int = Field(..., description='Hotel cost')
