from sqlalchemy.orm import Session
from app.domain.models.pasto import Pasto
from app.domain.models.enums import TipoPastagem
from app.domain.models.usuario import Usuario
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.services.plano_service import validar_limite

TAXA_LOTACAO = {
    TipoPastagem.BRACHIARIA: 1.2,
    TipoPastagem.MOMBACA: 3.0,
    TipoPastagem.TANZANIA: 2.5,
}


def calcular_capacidade(
    tamanho_ha: float,
    tipo_pastagem: TipoPastagem,
) -> int:
    taxa = TAXA_LOTACAO.get(tipo_pastagem, 1)
    return int(tamanho_ha * taxa)


def criar_pasto(
    db: Session,
    nome: str,
    tamanho_ha: float,
    tipo_pastagem: TipoPastagem,
    usuario: Usuario,
) -> Pasto:
    try:
        total_pastos = db.query(Pasto).filter(
            Pasto.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_pastos,
            limite=usuario.plano.limite_pastos,
            mensagem="Limite de pastos atingido para seu plano",
        )

        if tamanho_ha <= 0:
            raise DomainError("Tamanho do pasto deve ser maior que zero")

        capacidade = calcular_capacidade(
            tamanho_ha=tamanho_ha,
            tipo_pastagem=tipo_pastagem,
        )

        pasto = Pasto(
            nome=nome,
            tamanho_ha=tamanho_ha,
            tipo_pastagem=tipo_pastagem,
            capacidade_sugerida=capacidade,
            quantidade_atual=0,
            custo_total=0,
            custo_medio=0,
            status="ativo",
            usuario_id=usuario.id,
        )

        db.add(pasto)
        db.commit()
        db.refresh(pasto)
        logger.info("Pasto registrado: %s", pasto.id)
        return pasto
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registrar pasto")
        raise
