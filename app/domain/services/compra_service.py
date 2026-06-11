from sqlalchemy.orm import Session
from app.domain.models.compra import Compra
from app.domain.models.pasto import Pasto
from app.domain.models.conta_bancaria import ContaBancaria
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.services.movimentacao_service import registrar_movimentacao
from app.domain.services.plano_service import validar_limite
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from datetime import date
from decimal import Decimal


def criar_compra(
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
        total_compras = db.query(Compra).filter(
            Compra.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_compras,
            limite=usuario.plano.limite_compras,
            mensagem="Limite de compras atingido para seu plano",
        )

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

        if conta_id:
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id == conta_id,
                ContaBancaria.usuario_id == usuario.id,
            ).first()
            if not conta:
                raise DomainError("Conta bancária não encontrada")

        valor_total_dec = Decimal(str(valor_total))
        frete_dec = Decimal(str(frete or 0))
        custo_total = (valor_total_dec + frete_dec).quantize(Decimal("0.01"))
        valor_unitario = (custo_total / Decimal(quantidade)).quantize(Decimal("0.01"))

        pasto.quantidade_atual += quantidade
        pasto.custo_total = (
            Decimal(str(pasto.custo_total)) + custo_total
        ).quantize(Decimal("0.01"))
        pasto.custo_medio = (
            pasto.custo_total / Decimal(pasto.quantidade_atual)
        ).quantize(Decimal("0.01"))

        compra = Compra(
            data=data,
            pasto_id=pasto_id,
            quantidade=quantidade,
            valor_total=valor_total,
            valor_unitario=valor_unitario,
            frete=frete,
            conta_id=conta_id,
            usuario_id=usuario.id,
        )

        db.add(compra)
        db.flush()  # gera compra.id sem commitar

        if conta_id:
            registrar_movimentacao(
                db=db,
                data=data,
                tipo="saida",
                descricao=f"Compra de gado - Pasto {pasto.nome}",
                valor=float(custo_total),
                conta_id=conta_id,
                usuario=usuario,
                compra_id=compra.id,  # FK direta para a compra
            )

        db.commit()
        db.refresh(compra)

        alerta = pasto.quantidade_atual > pasto.capacidade_sugerida
        logger.info("Compra %s registrada no pasto %s", compra.id, pasto.id)
        return compra, alerta

    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao registrar compra")
        raise


def listar_compras(
    db: Session,
    usuario: Usuario,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[Compra]:
    query = db.query(Compra).filter(Compra.usuario_id == usuario.id)
    if data_inicio:
        query = query.filter(Compra.data >= data_inicio)
    if data_fim:
        query = query.filter(Compra.data <= data_fim)
    return query.order_by(Compra.data.desc()).all()


def buscar_compra(db: Session, compra_id: int, usuario: Usuario) -> Compra:
    compra = db.query(Compra).filter(
        Compra.id == compra_id,
        Compra.usuario_id == usuario.id,
    ).first()
    if not compra:
        raise DomainError("Compra não encontrada")
    return compra


def excluir_compra(db: Session, compra_id: int, usuario: Usuario) -> None:
    try:
        compra = buscar_compra(db, compra_id, usuario)

        pasto = db.query(Pasto).filter(
            Pasto.id == compra.pasto_id,
            Pasto.usuario_id == usuario.id,
        ).first()

        if not pasto:
            raise DomainError("Pasto vinculado à compra não foi encontrado")

        if compra.quantidade > pasto.quantidade_atual:
            raise DomainError(
                f"Não é possível excluir esta compra: ela adicionou {compra.quantidade} "
                f"animal(is) ao pasto '{pasto.nome}', mas o estoque atual é de apenas "
                f"{pasto.quantidade_atual}. Parte desses animais já foi vendida ou "
                "movimentada — exclua as vendas/movimentações relacionadas primeiro."
            )

        frete = Decimal(str(compra.frete or 0))
        custo_da_compra = (
            Decimal(str(compra.valor_total)) + frete
        ).quantize(Decimal("0.01"))

        pasto.quantidade_atual -= compra.quantidade
        pasto.custo_total = (
            Decimal(str(pasto.custo_total)) - custo_da_compra
        ).quantize(Decimal("0.01"))

        if pasto.quantidade_atual > 0:
            pasto.custo_medio = (
                pasto.custo_total / Decimal(pasto.quantidade_atual)
            ).quantize(Decimal("0.01"))
        else:
            pasto.custo_medio = Decimal("0.00")
            pasto.custo_total = Decimal("0.00")

        if compra.conta_id:
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id == compra.conta_id,
                ContaBancaria.usuario_id == usuario.id,
            ).first()

            if conta:
                conta.saldo = (
                    Decimal(str(conta.saldo)) + custo_da_compra
                ).quantize(Decimal("0.01"))

            db.query(MovimentacaoFinanceira).filter(
                MovimentacaoFinanceira.compra_id == compra.id,
                MovimentacaoFinanceira.usuario_id == usuario.id,
            ).delete(synchronize_session=False)

        db.delete(compra)
        db.commit()
        logger.info("Compra %s excluída com reversão no pasto %s", compra_id, pasto.id)

    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao excluir compra %s", compra_id)
        raise