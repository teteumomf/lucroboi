from sqlalchemy.orm import Session
from app.domain.models.conta_bancaria import ContaBancaria
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite

def criar_conta(
    db: Session,
    nome: str,
    saldo_inicial: float,
    usuario: Usuario
):
    try:
        total_conta = db.query(ContaBancaria).filter(
            ContaBancaria.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_conta,
            limite=usuario.plano.limite_contas,
            mensagem="Limite de contas bancárias atingido para seu plano",
        )

        conta = ContaBancaria(
            nome=nome,
            saldo=saldo_inicial,
            usuario_id=usuario.id,
        )

        db.add(conta)
        db.commit()
        db.refresh(conta)
        logger.info("Conta registrada: %s", conta.id)
        return conta
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registrar conta")
        raise