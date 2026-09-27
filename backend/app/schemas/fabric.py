from pydantic import BaseModel, Field

class FabricHemUpdate(BaseModel):
    hem_top: float = Field(ge=0)
    hem_bottom: float = Field(ge=0)
