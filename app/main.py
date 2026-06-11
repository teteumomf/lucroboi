from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa todos os models antes das rotas para o SQLAlchemy
# resolver os relacionamentos corretamente
import app.domain.models  # noqa: F401

from app.api.routes import (
    usuarios, pastos, compras, vendas,
    despesas, financeiro, movimentacoes_gado, relatorios,
)

app = FastAPI(
    title="LucroBoi",
    description="API de gestão de gado de corte",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "http://10.0.2.2",
        "http://10.0.2.2:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(pastos.router)
app.include_router(compras.router)
app.include_router(vendas.router)
app.include_router(despesas.router)
app.include_router(financeiro.router)
app.include_router(movimentacoes_gado.router)
app.include_router(relatorios.router)