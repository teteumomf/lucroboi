from datetime import date
from pydantic import BaseModel


class MovimentacaoGadoCreate(BaseModel):
    data: date
    pasto_origem_id: int
    pasto_destino_id: int
    quantidade: int


class MovimentacaoGadoResponse(BaseModel):
    id: int
    data: date
    pasto_origem_id: int
    pasto_destino_id: int
    quantidade: int
    custo_unitario: float

    class Config:
        from_attributes = True