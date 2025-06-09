from pydantic import BaseModel

class BoundaryTemps(BaseModel):
    top: float
    bottom: float
    left: float
    right: float

class HeatRequest(BaseModel):
    width: int
    height: int
    boundaryTemps: BoundaryTemps