from sqlalchemy import (
    Integer, Date, Numeric, ForeignKey, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Venda(Base):
    __tablename__ = "vendas"

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

    pasto_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pastos.id"), nullable=False
    )

    quantidade: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    valor_total: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    valor_unitario: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    frete: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    custo_unitario: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    custo_total: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    conta_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("contas_bancarias.id"), nullable=True
    )

    lucro_bruto: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )