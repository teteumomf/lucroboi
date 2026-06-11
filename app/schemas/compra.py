from datetime import date
from pydantic import BaseModel


class CompraCreate(BaseModel):
    data: date
    pasto_id: int
    quantidade: int
    conta_id: int | None
    frete: float | None
    valor_total: float


class CompraResponse(BaseModel):
    id: int
    data: date
    pasto_id: int
    quantidade: int
    valor_total: float
    valor_unitario: float
    alerta_capacidade: bool | None = None

    class Config:
        from_attributes = True