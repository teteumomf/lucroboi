from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.domain.models.enums import TipoPastagem


class Pasto(Base):
    __tablename__ = "pastos"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    usuario_id = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )

    usuario = relationship("Usuario")

    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    tamanho_ha: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    tipo_pastagem: Mapped[TipoPastagem] = mapped_column(
        SqlEnum(TipoPastagem), nullable=False
    )

    capacidade_sugerida: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    quantidade_atual: Mapped[int] = mapped_column(
        Integer, default=0
    )

    custo_total: Mapped[float] = mapped_column(
        Numeric(12, 2), default=0
    )

    custo_medio: Mapped[float] = mapped_column(
        Numeric(12, 2), default=0
    )

    status: Mapped[str] = mapped_column(
        String(20), default="ativo"
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )