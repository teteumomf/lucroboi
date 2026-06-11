from datetime import date
from pydantic import BaseModel


class VendaCreate(BaseModel):
    data: date
    pasto_id: int
    quantidade: int
    conta_id: int | None
    frete: float | None
    valor_total: float


class VendaResponse(BaseModel):
    id: int
    data: date
    pasto_id: int
    quantidade: int
    valor_total: float
    valor_unitario: float
    custo_unitario: float
    custo_total: float
    lucro_bruto: float

    class Config:
        from_attributes = True