from datetime import date
from pydantic import BaseModel


class DespesaCreate(BaseModel):
    data: date
    descricao: str
    valor: float
    conta_id: int | None
    pasto_id: int | None = None


class DespesaResponse(BaseModel):
    id: int
    data: date
    descricao: str
    valor: float
    pasto_id: int | None

    class Config:
        from_attributes = True