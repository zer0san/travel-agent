from pydantic import BaseModel, Field

class Location(BaseModel):
    longitude: float = Field(..., title='Longitude', ge=-180, le=180)
    latitude: float = Field(..., title='Latitude', ge=-90, le=90)