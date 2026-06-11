from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.core.database import Base


class ContaBancaria(Base):
    __tablename__ = "contas_bancarias"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    usuario_id = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )

    usuario = relationship("Usuario")

    nome: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    saldo: Mapped[float] = mapped_column(
        Numeric(14, 2), default=0
    )

    # FIX: datetime.utcnow deprecated no Python 3.12+
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
