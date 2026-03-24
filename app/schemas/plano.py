from pydantic import BaseModel


class PlanoResponse(BaseModel):
    id: int
    nome: str

    limite_contas: int | None
    limite_pastos: int | None
    limite_vendas: int | None
    limite_compras: int | None
    limite_despesas: int | None
    limite_movimentacoes: int | None

    relatorio_resumo: bool
    relatorio_por_pasto: bool
    relatorio_fluxo_caixa: bool
    relatorio_dre: bool

    class Config:
        from_attributes = True