from sqlalchemy.orm import Session
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.models.conta_bancaria import ContaBancaria
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite

def registrar_movimentacao(
    db: Session,
    data,
    tipo: str,
    descricao: str,
    valor: float,
    conta_id: int,
    usuario: Usuario
):
    try:
        total_movimentacoes = db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_movimentacoes,
            limite=usuario.plano.limite_movimentacoes,
            mensagem="Limite de movimentações atingido para seu plano",
        )
        conta = db.get(ContaBancaria, conta_id)

        if not conta:
            raise DomainError("Conta bancária não encontrada")

        if tipo == "entrada":
            conta.saldo += valor
        elif tipo == "saida":
            conta.saldo -= valor
        else:
            raise DomainError("Tipo de movimentação inválido")

        movimentacao = MovimentacaoFinanceira(
            data=data,
            tipo=tipo,
            descricao=descricao,
            valor=valor,
            conta_id=conta_id,
            usuario_id=usuario.id,
        )

        db.add(movimentacao)
        db.commit()
        db.refresh(movimentacao)
        logger.info("Movimentação registrada: %s", movimentacao.id)
        return movimentacao
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registrar movimentação")
        raise