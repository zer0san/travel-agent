from pydantic import BaseModel, Field

class Budget(BaseModel):
    '''information about budget'''
    attraction_budget: int = Field(default=0, description='Budget for attractions')
    meal_budget: int = Field(default=0, description='Budget for meals')
    hotel_budget: int = Field(default=0, description='Budget for hotels')
    transportation_budget: int = Field(default=0, description='Budget for transportation')
    total_budget: int = Field(..., description='Total budget')
