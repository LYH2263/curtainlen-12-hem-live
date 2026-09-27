from pydantic import BaseModel, Field

class FabricHemUpdate(BaseModel):
    hem_top: float = Field(ge=0, allow_inf_nan=False)
    hem_bottom: float = Field(ge=0, allow_inf_nan=False)
