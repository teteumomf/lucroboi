from sqlalchemy import (
    Integer, Date, Numeric, String, ForeignKey, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from sqlalchemy.orm import relationship
from app.core.database import Base


class MovimentacaoFinanceira(Base):
    __tablename__ = "movimentacoes_financeiras"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    usuario_id = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )

    usuario = relationship("Usuario")

    data: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(10), nullable=False  # entrada | saida
    )

    descricao: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    valor: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    conta_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contas_bancarias.id"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )