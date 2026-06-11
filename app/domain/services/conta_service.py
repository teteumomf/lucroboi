from sqlalchemy.orm import Session
from app.domain.models.conta_bancaria import ContaBancaria
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.models.compra import Compra
from app.domain.models.venda import Venda
from app.domain.models.despesa import Despesa
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite


def criar_conta(
    db: Session,
    nome: str,
    saldo_inicial: float,
    usuario: Usuario,
):
    try:
        total_contas = db.query(ContaBancaria).filter(
            ContaBancaria.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_contas,
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
        logger.error("Erro ao registrar conta")
        raise


def listar_contas(db: Session, usuario: Usuario) -> list[ContaBancaria]:
    return (
        db.query(ContaBancaria)
        .filter(ContaBancaria.usuario_id == usuario.id)
        .order_by(ContaBancaria.nome)
        .all()
    )


def buscar_conta(db: Session, conta_id: int, usuario: Usuario) -> ContaBancaria:
    conta = db.query(ContaBancaria).filter(
        ContaBancaria.id == conta_id,
        ContaBancaria.usuario_id == usuario.id,
    ).first()

    if not conta:
        raise DomainError("Conta bancária não encontrada")

    return conta


def editar_conta(
    db: Session,
    conta_id: int,
    usuario: Usuario,
    nome: str | None = None,
) -> ContaBancaria:
    try:
        conta = buscar_conta(db, conta_id, usuario)

        if nome is not None:
            conta.nome = nome

        db.commit()
        db.refresh(conta)
        logger.info("Conta editada: %s", conta.id)
        return conta
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao editar conta")
        raise


def excluir_conta(db: Session, conta_id: int, usuario: Usuario) -> None:
    try:
        conta = buscar_conta(db, conta_id, usuario)

        if float(conta.saldo) != 0:
            raise DomainError(
                f"Não é possível excluir a conta '{conta.nome}' pois ela "
                f"possui saldo de R$ {float(conta.saldo):.2f}. "
                "Zere o saldo antes de excluir."
            )

        # Bloqueia se houver qualquer registro vinculado
        tem_movimentacoes = db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.conta_id == conta_id
        ).first()
        if tem_movimentacoes:
            raise DomainError(
                f"Não é possível excluir a conta '{conta.nome}' pois ela "
                "possui movimentações financeiras vinculadas."
            )

        tem_compras = db.query(Compra).filter(Compra.conta_id == conta_id).first()
        if tem_compras:
            raise DomainError(
                f"Não é possível excluir a conta '{conta.nome}' pois ela "
                "possui compras vinculadas."
            )

        tem_vendas = db.query(Venda).filter(Venda.conta_id == conta_id).first()
        if tem_vendas:
            raise DomainError(
                f"Não é possível excluir a conta '{conta.nome}' pois ela "
                "possui vendas vinculadas."
            )

        tem_despesas = db.query(Despesa).filter(Despesa.conta_id == conta_id).first()
        if tem_despesas:
            raise DomainError(
                f"Não é possível excluir a conta '{conta.nome}' pois ela "
                "possui despesas vinculadas."
            )

        db.delete(conta)
        db.commit()
        logger.info("Conta excluída: %s", conta_id)
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao excluir conta")
        raise
