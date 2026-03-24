from pydantic import BaseModel
from app.domain.models.enums import TipoPastagem


class PastoCreate(BaseModel):
    nome: str
    tamanho_ha: float
    tipo_pastagem: TipoPastagem


class PastoResponse(BaseModel):
    id: int
    nome: str
    tamanho_ha: float
    tipo_pastagem: TipoPastagem
    capacidade_sugerida: int
    quantidade_atual: int
    custo_total: float
    custo_medio: float
    status: str

    class Config:
        from_attributes = True