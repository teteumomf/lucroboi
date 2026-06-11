# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.domain.models.usuario import Usuario
from app.domain.models.plano import Plano

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def plano_completo(db):
    plano = Plano(
        nome="Completo",
        limite_contas=None,
        limite_pastos=None,
        limite_compras=None,
        limite_vendas=None,
        limite_despesas=None,
        limite_movimentacoes=None,
        relatorio_resumo=True,
        relatorio_por_pasto=True,
        relatorio_fluxo_caixa=True,
        relatorio_dre=True,
        # FIX: campos que faltavam — causavam AttributeError nos testes dos relatórios novos
        relatorio_evolucao_patrimonio=True,
        relatorio_resultado_mensal=True,
        relatorio_giro_animais=True,
        relatorio_ranking_pastos=True,
    )
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return plano


@pytest.fixture
def usuario(db, plano_completo):
    usuario = Usuario(
        nome="Teste",
        email="teste@teste.com",
        senha_hash="hash",
        plano_id=plano_completo.id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
