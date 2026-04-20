from typing import List, Optional

from pydantic import BaseModel, Field

class TripPlanRequest(BaseModel):
    city: str = Field(..., description="The city for which to plan the trip", examples=["北京"])
    start_date: str = Field(..., description="The start date of the trip", examples=["2026-01-01"])
    end_date: str = Field(..., description="The end date of the trip", examples=["2030-01-03"])
    transportation: str = Field(...,description="The transportation type of the trip", examples=["公共交通"])
    accommodation: Optional[str] = Field(None, description="The accommodation type of the trip", examples=["经济型酒店"])
    preferences: List[str] = Field(..., description="The preferences type of the trip", examples=[['文化', '美食']])
    additional_request: Optional[str] = Field(None, description="The additional request for the trip", examples=["请安排一些适合孩子的活动"])
