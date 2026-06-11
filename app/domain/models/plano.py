from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Plano(Base):
    __tablename__ = "planos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    # Limites (None = ilimitado)
    limite_contas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_pastos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_vendas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_compras: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_despesas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_movimentacoes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Permissões de relatórios
    relatorio_resumo: Mapped[bool] = mapped_column(Boolean, default=True)
    relatorio_por_pasto: Mapped[bool] = mapped_column(Boolean, default=False)
    relatorio_fluxo_caixa: Mapped[bool] = mapped_column(Boolean, default=False)
    relatorio_dre: Mapped[bool] = mapped_column(Boolean, default=False)
    relatorio_evolucao_patrimonio: Mapped[bool] = mapped_column(Boolean, default=False)
    relatorio_resultado_mensal: Mapped[bool] = mapped_column(Boolean, default=False)
    relatorio_giro_animais: Mapped[bool] = mapped_column(Boolean, default=False)
    relatorio_ranking_pastos: Mapped[bool] = mapped_column(Boolean, default=False)