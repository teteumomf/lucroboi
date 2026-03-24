from sqlalchemy import (
    Integer, Date, ForeignKey, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime

from app.core.database import Base
from sqlalchemy.orm import relationship

class MovimentacaoGado(Base):
    __tablename__ = "movimentacoes_gado"

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

    pasto_origem_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pastos.id"), nullable=False
    )

    pasto_destino_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pastos.id"), nullable=False
    )

    quantidade: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    custo_unitario: Mapped[float] = mapped_column(
        Integer, nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )