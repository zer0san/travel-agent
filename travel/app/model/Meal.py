from typing import Optional

from pydantic import BaseModel, Field

from app.model.Location import Location


class Meal(BaseModel):
    '''information about meal'''
    type: str = Field(..., description='Type of meal(breakfast/lunch/dinner/snack)')
    name: str = Field(..., description='Name of meal')
    address: str = Field(..., description='Address of meal')
    location: Optional[Location] = Field(default=None, description='Location of meal')
    description: Optional[str] = Field(default=None, description='Description of meal')
    cost: float = Field(..., description='Cost of meal')
