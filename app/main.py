from fastapi import FastAPI
from app.api.routes import (
    pastos, compras, vendas, despesas, financeiro, movimentacoes_gado, relatorios
)

app = FastAPI(title="LucroBoi")

app.include_router(pastos.router)
app.include_router(compras.router)
app.include_router(vendas.router)
app.include_router(despesas.router)
app.include_router(financeiro.router)
app.include_router(movimentacoes_gado.router)
app.include_router(relatorios.router)