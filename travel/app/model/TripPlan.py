from typing import List, Optional

from pydantic import BaseModel, Field

from app.model.Budget import Budget
from app.model.DayPlan import DayPlan
from app.model.Weather import Weather


class TripPlan(BaseModel):
    '''information about trip plan'''
    city: str = Field(..., title='target city')
    start_date: str = Field(..., description='start date of trip plan')
    end_date: str = Field(..., description='end date of trip plan')
    days: List[DayPlan] = Field(..., description='the plan of each day')
    weather_condition: List[Weather] = Field(..., description='the weather condition of each day')
    overall_suggestion: str = Field(..., description='the overall suggestion of the trip plan')
    budget: Optional[Budget] = Field(default=None, description='the budget of the trip plan')

    