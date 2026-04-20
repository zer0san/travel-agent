from typing import List, Optional

from pydantic import BaseModel, Field

from app.model.Attraction import Attraction
from app.model.Hotel import Hotel
from app.model.Meal import Meal

class DayPlan(BaseModel):
    date: str = Field(..., description='the start date')
    day_index: int = Field(..., description='the index of the day(start with 0)')
    description: str = Field(..., description='the plan of the day')
    transportation: int = Field(..., description='the transportation')
    accommodation: str = Field(..., description='the accommodation arrangement')
    hotel: Optional[Hotel] = Field(default=None, description='the hotel info')
    attraction: List[Attraction] = Field(default=None, description='the attraction list')
    meals: List[Meal] = Field(default=None, description='the meals list')