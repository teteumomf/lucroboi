from sqlalchemy.orm import Session
from app.domain.models.venda import Venda
from app.domain.models.pasto import Pasto
from app.domain.models.conta_bancaria import ContaBancaria
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.services.movimentacao_service import registrar_movimentacao
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
from datetime import date
from decimal import Decimal


def criar_venda(
    db: Session,
    data,
    pasto_id: int,
    quantidade: int,
    valor_total: float,
    usuario: Usuario,
    conta_id: int,
    frete: float = 0.0,
):
    try:
        total_vendas = db.query(Venda).filter(
            Venda.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_vendas,
            limite=usuario.plano.limite_vendas,
            mensagem="Limite de vendas atingido para seu plano",
        )

        conta = db.query(ContaBancaria).filter(
            ContaBancaria.id == conta_id,
            ContaBancaria.usuario_id == usuario.id,
        ).first()

        if not conta:
            raise DomainError("Conta bancária não encontrada")

        if quantidade <= 0:
            raise DomainError("Quantidade deve ser maior que zero")

        if valor_total <= 0:
            raise DomainError("Valor total deve ser maior que zero")

        if isinstance(data, str):
            data = date.fromisoformat(data)

        pasto = db.query(Pasto).filter(
            Pasto.id == pasto_id,
            Pasto.usuario_id == usuario.id,
        ).first()

        if not pasto:
            raise DomainError("Pasto não encontrado")

        if quantidade > pasto.quantidade_atual:
            raise DomainError("Quantidade maior que o estoque disponível no pasto")

        valor_total_d = Decimal(str(valor_total))
        frete_d = Decimal(str(frete or 0))
        quantidade_d = Decimal(quantidade)

        valor_unitario = (valor_total_d / quantidade_d).quantize(Decimal("0.01"))
        custo_unitario = Decimal(str(pasto.custo_medio))
        custo_total = (custo_unitario * quantidade_d).quantize(Decimal("0.01"))
        lucro_bruto = (valor_total_d - custo_total - frete_d).quantize(Decimal("0.01"))

        venda = Venda(
            data=data,
            pasto_id=pasto_id,
            quantidade=quantidade,
            valor_total=valor_total,
            valor_unitario=valor_unitario,
            custo_unitario=custo_unitario,
            custo_total=custo_total,
            lucro_bruto=lucro_bruto,
            frete=frete,
            conta_id=conta_id,
            usuario_id=usuario.id,
        )

        pasto.quantidade_atual -= quantidade
        pasto.custo_total = (
            Decimal(str(pasto.custo_total)) - custo_total
        ).quantize(Decimal("0.01"))

        if pasto.quantidade_atual > 0:
            pasto.custo_medio = (
                pasto.custo_total / Decimal(pasto.quantidade_atual)
            ).quantize(Decimal("0.01"))
        else:
            pasto.custo_medio = Decimal("0.00")
            pasto.custo_total = Decimal("0.00")

        db.add(venda)
        db.commit()

        registrar_movimentacao(
            db=db,
            data=data,
            tipo="entrada",
            descricao=f"Venda de gado - Pasto {pasto.id}",
            valor=valor_total,
            conta_id=conta_id,
            usuario=usuario,
        )

        db.refresh(venda)
        logger.info("Venda registrada no pasto %s", pasto.id)
        return venda
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao registrar venda")
        raise


def listar_vendas(db: Session, usuario: Usuario) -> list[Venda]:
    return (
        db.query(Venda)
        .filter(Venda.usuario_id == usuario.id)
        .order_by(Venda.data.desc())
        .all()
    )


def buscar_venda(db: Session, venda_id: int, usuario: Usuario) -> Venda:
    venda = db.query(Venda).filter(
        Venda.id == venda_id,
        Venda.usuario_id == usuario.id,
    ).first()

    if not venda:
        raise DomainError("Venda não encontrada")

    return venda


def excluir_venda(db: Session, venda_id: int, usuario: Usuario) -> None:
    """
    Reverte o efeito da venda:
    - Devolve os animais ao estoque do pasto
    - Recalcula custo_total e custo_medio do pasto com base no custo_unitario
      registrado no momento da venda (snapshot histórico confiável)
    - Debita o valor da venda da conta bancária (estorno da entrada)
    - Remove a movimentação financeira de entrada gerada pela venda
    """
    try:
        venda = buscar_venda(db, venda_id, usuario)

        pasto = db.query(Pasto).filter(
            Pasto.id == venda.pasto_id,
            Pasto.usuario_id == usuario.id,
        ).first()

        if not pasto:
            raise DomainError("Pasto vinculado à venda não foi encontrado")

        custo_unitario = Decimal(str(venda.custo_unitario))
        custo_total_venda = Decimal(str(venda.custo_total))
        valor_venda = Decimal(str(venda.valor_total))

        # Devolve animais ao pasto
        pasto.quantidade_atual += venda.quantidade
        pasto.custo_total = (
            Decimal(str(pasto.custo_total)) + custo_total_venda
        ).quantize(Decimal("0.01"))
        pasto.custo_medio = (
            pasto.custo_total / Decimal(pasto.quantidade_atual)
        ).quantize(Decimal("0.01"))

        # Estorna o valor da conta bancária (se havia conta vinculada)
        if venda.conta_id:
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id == venda.conta_id,
                ContaBancaria.usuario_id == usuario.id,
            ).first()

            if conta:
                conta.saldo = (
                    Decimal(str(conta.saldo)) - valor_venda
                ).quantize(Decimal("0.01"))

            # Remove a movimentação financeira de entrada gerada pela venda
            db.query(MovimentacaoFinanceira).filter(
                MovimentacaoFinanceira.conta_id == venda.conta_id,
                MovimentacaoFinanceira.tipo == "entrada",
                MovimentacaoFinanceira.data == venda.data,
                MovimentacaoFinanceira.valor == venda.valor_total,
                MovimentacaoFinanceira.usuario_id == usuario.id,
            ).delete(synchronize_session=False)

        db.delete(venda)
        db.commit()
        logger.info("Venda %s excluída com reversão no pasto %s", venda_id, pasto.id)
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao excluir venda %s", venda_id)
        raise
