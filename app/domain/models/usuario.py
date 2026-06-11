from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    nome: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean, default=True
    )

    # FIX: datetime.utcnow deprecated no Python 3.12+
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    plano_id = mapped_column(
        Integer, ForeignKey("planos.id"), nullable=False
    )

    plano = relationship("Plano")
