from sqlalchemy.orm import Session
from app.domain.models.despesa import Despesa
from app.domain.models.pasto import Pasto
from app.domain.services.movimentacao_service import registrar_movimentacao
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
from app.domain.models.conta_bancaria import ContaBancaria

def criar_despesa(
    db: Session,
    data,
    descricao: str,
    valor: float,
    usuario: Usuario,
    conta_id: int,
    pasto_id: int | None = None,
):
    try:
        total_despesas = db.query(Despesa).filter(
            Despesa.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_despesas,
            limite=usuario.plano.limite_despesas,
            mensagem="Limite de despesas atingido para seu plano",
        )

        conta = db.query(ContaBancaria).filter(
            ContaBancaria.id == conta_id,
            ContaBancaria.usuario_id == usuario.id
        ).first()

        if not conta:
            raise DomainError("Conta bancária não encontrada")

        if conta.saldo < valor:
            raise DomainError("Saldo insuficiente na conta")

        if valor <= 0:
            raise DomainError("Valor da despesa deve ser maior que zero")

        despesa = Despesa(
            data=data,
            descricao=descricao,
            valor=valor,
            conta_id=conta.id,
            pasto_id=pasto_id,
            usuario_id=usuario.id,
        )

        # Atualiza saldo
        conta.saldo -= valor

        # Se for despesa vinculada a pasto, impacta custo
        if pasto_id:
            pasto = db.get(Pasto, pasto_id)

            if not pasto:
                raise DomainError("Pasto não encontrado")

            if pasto.quantidade_atual > 0:
                pasto.custo_total += valor
                pasto.custo_medio = round(
                    pasto.custo_total / pasto.quantidade_atual, 2
                )

        db.add(despesa)
        db.commit()
        registrar_movimentacao(
            db=db,
            data=data,
            tipo="saida",
            descricao=descricao,
            valor=valor,
            conta_id=conta.id,
            usuario_id=usuario.id
        )
        db.refresh(despesa)
        logger.info("Despesa registrada: %s", despesa.id)
        return despesa
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registrar despesa")
        raise