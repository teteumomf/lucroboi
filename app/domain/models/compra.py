from sqlalchemy import (
    Integer, Date, Numeric, ForeignKey, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime

from app.core.database import Base
from sqlalchemy.orm import relationship

class Compra(Base):
    __tablename__ = "compras"

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

    conta_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("contas_bancarias.id"), nullable=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )