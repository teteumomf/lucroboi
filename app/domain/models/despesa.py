from sqlalchemy import (
    Integer, Date, Numeric, ForeignKey, String, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Despesa(Base):
    __tablename__ = "despesas"

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

    descricao: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    valor: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    pasto_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pastos.id"), nullable=True
    )

    conta_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("contas_bancarias.id"), nullable=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )