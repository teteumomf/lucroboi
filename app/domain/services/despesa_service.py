from sqlalchemy.orm import Session
from app.domain.models.despesa import Despesa
from app.domain.models.pasto import Pasto
from app.domain.models.conta_bancaria import ContaBancaria
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.services.movimentacao_service import registrar_movimentacao
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
from decimal import Decimal
from datetime import date


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

        if valor <= 0:
            raise DomainError("Valor da despesa deve ser maior que zero")

        conta = db.query(ContaBancaria).filter(
            ContaBancaria.id == conta_id,
            ContaBancaria.usuario_id == usuario.id,
        ).first()

        if not conta:
            raise DomainError("Conta bancária não encontrada")

        if conta.saldo < valor:
            raise DomainError("Saldo insuficiente na conta")

        despesa = Despesa(
            data=data,
            descricao=descricao,
            valor=valor,
            conta_id=conta.id,
            pasto_id=pasto_id,
            usuario_id=usuario.id,
        )

        conta.saldo = (
            Decimal(str(conta.saldo)) - Decimal(str(valor))
        ).quantize(Decimal("0.01"))

        if pasto_id:
            pasto = db.query(Pasto).filter(
                Pasto.id == pasto_id,
                Pasto.usuario_id == usuario.id,
            ).first()

            if not pasto:
                raise DomainError("Pasto não encontrado")

            if pasto.quantidade_atual > 0:
                pasto.custo_total = (
                    Decimal(str(pasto.custo_total)) + Decimal(str(valor))
                ).quantize(Decimal("0.01"))
                pasto.custo_medio = (
                    pasto.custo_total / Decimal(pasto.quantidade_atual)
                ).quantize(Decimal("0.01"))

        db.add(despesa)
        db.commit()
        db.refresh(despesa)

        registrar_movimentacao(
            db=db,
            data=data,
            tipo="saida",
            descricao=descricao,
            valor=valor,
            conta_id=conta.id,
            usuario=usuario,
        )

        logger.info("Despesa registrada: %s", despesa.id)
        return despesa
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao registrar despesa")
        raise


def listar_despesas(db: Session, usuario: Usuario) -> list[Despesa]:
    return (
        db.query(Despesa)
        .filter(Despesa.usuario_id == usuario.id)
        .order_by(Despesa.data.desc())
        .all()
    )


def buscar_despesa(db: Session, despesa_id: int, usuario: Usuario) -> Despesa:
    despesa = db.query(Despesa).filter(
        Despesa.id == despesa_id,
        Despesa.usuario_id == usuario.id,
    ).first()

    if not despesa:
        raise DomainError("Despesa não encontrada")

    return despesa


def excluir_despesa(db: Session, despesa_id: int, usuario: Usuario) -> None:
    """
    Reverte o efeito da despesa:
    - Devolve o valor ao saldo da conta bancária
    - Se estava vinculada a um pasto, desconta do custo_total e recalcula custo_medio
    - Remove a movimentação financeira de saída gerada pela despesa
    """
    try:
        despesa = buscar_despesa(db, despesa_id, usuario)
        valor = Decimal(str(despesa.valor))

        # Devolve saldo à conta
        if despesa.conta_id:
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id == despesa.conta_id,
                ContaBancaria.usuario_id == usuario.id,
            ).first()

            if conta:
                conta.saldo = (
                    Decimal(str(conta.saldo)) + valor
                ).quantize(Decimal("0.01"))

            # Remove movimentação de saída vinculada
            db.query(MovimentacaoFinanceira).filter(
                MovimentacaoFinanceira.conta_id == despesa.conta_id,
                MovimentacaoFinanceira.tipo == "saida",
                MovimentacaoFinanceira.data == despesa.data,
                MovimentacaoFinanceira.valor == despesa.valor,
                MovimentacaoFinanceira.usuario_id == usuario.id,
            ).delete(synchronize_session=False)

        # Reverte impacto no custo do pasto (se vinculado)
        if despesa.pasto_id:
            pasto = db.query(Pasto).filter(
                Pasto.id == despesa.pasto_id,
                Pasto.usuario_id == usuario.id,
            ).first()

            if pasto and pasto.quantidade_atual > 0:
                pasto.custo_total = (
                    Decimal(str(pasto.custo_total)) - valor
                ).quantize(Decimal("0.01"))
                pasto.custo_medio = (
                    pasto.custo_total / Decimal(pasto.quantidade_atual)
                ).quantize(Decimal("0.01"))

        db.delete(despesa)
        db.commit()
        logger.info("Despesa %s excluída com reversão", despesa_id)
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao excluir despesa %s", despesa_id)
        raise
