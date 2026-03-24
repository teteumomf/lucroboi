from datetime import date
from pydantic import BaseModel


class ContaCreate(BaseModel):
    nome: str
    saldo_inicial: float = 0


class ContaResponse(BaseModel):
    id: int
    nome: str
    saldo: float

    class Config:
        from_attributes = True


class MovimentacaoResponse(BaseModel):
    id: int
    data: date
    tipo: str
    descricao: str
    valor: float
    conta_id: int

    class Config:
        from_attributes = True