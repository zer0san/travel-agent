from pydantic import BaseModel, Field, field_validator


class Weather(BaseModel):
    day_temperature: float = Field(..., description='Temperature of day(Celsius)')
    day_weather: str = Field(..., description='Weather of day')
    night_temperature: float = Field(..., description="Temperature of night(Celsius)")
    night_weather: str = Field(..., description="Weather of night")
    date: str = Field(..., description="Date")
    wind_direction: str = Field(..., description="wind direction")
    wind_power: str = Field(..., description="wind power")

    @field_validator('day_temperature', 'night_temperature', mode='before')
    def parse_temperature(cls, v):
        if isinstance(v, str):
            v = v.replace('°C','').replace('℃','').replace('°','').strip()
        return v