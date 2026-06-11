from sqlalchemy.orm import Session
from app.domain.models.venda import Venda
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

        db.add(venda)
        db.flush()  # gera venda.id sem commitar

        registrar_movimentacao(
            db=db,
            data=data,
            tipo="entrada",
            descricao=f"Venda de gado - Pasto {pasto.nome}",
            valor=valor_total,
            conta_id=conta_id,
            usuario=usuario,
            venda_id=venda.id,  # FK direta para a venda
        )

        db.commit()
        db.refresh(venda)
        logger.info("Venda %s registrada no pasto %s", venda.id, pasto.id)
        return venda

    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao registrar venda")
        raise


def listar_vendas(
    db: Session,
    usuario: Usuario,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[Venda]:
    query = db.query(Venda).filter(Venda.usuario_id == usuario.id)
    if data_inicio:
        query = query.filter(Venda.data >= data_inicio)
    if data_fim:
        query = query.filter(Venda.data <= data_fim)
    return query.order_by(Venda.data.desc()).all()


def buscar_venda(db: Session, venda_id: int, usuario: Usuario) -> Venda:
    venda = db.query(Venda).filter(
        Venda.id == venda_id,
        Venda.usuario_id == usuario.id,
    ).first()
    if not venda:
        raise DomainError("Venda não encontrada")
    return venda


def excluir_venda(db: Session, venda_id: int, usuario: Usuario) -> None:
    try:
        venda = buscar_venda(db, venda_id, usuario)

        pasto = db.query(Pasto).filter(
            Pasto.id == venda.pasto_id,
            Pasto.usuario_id == usuario.id,
        ).first()

        if not pasto:
            raise DomainError("Pasto vinculado à venda não foi encontrado")

        custo_total_venda = Decimal(str(venda.custo_total))
        valor_venda = Decimal(str(venda.valor_total))

        pasto.quantidade_atual += venda.quantidade
        pasto.custo_total = (
            Decimal(str(pasto.custo_total)) + custo_total_venda
        ).quantize(Decimal("0.01"))
        pasto.custo_medio = (
            pasto.custo_total / Decimal(pasto.quantidade_atual)
        ).quantize(Decimal("0.01"))

        if venda.conta_id:
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id == venda.conta_id,
                ContaBancaria.usuario_id == usuario.id,
            ).first()

            if conta:
                conta.saldo = (
                    Decimal(str(conta.saldo)) - valor_venda
                ).quantize(Decimal("0.01"))

            db.query(MovimentacaoFinanceira).filter(
                MovimentacaoFinanceira.venda_id == venda.id,
                MovimentacaoFinanceira.usuario_id == usuario.id,
            ).delete(synchronize_session=False)

        db.delete(venda)
        db.commit()
        logger.info("Venda %s excluída com reversão", venda_id)

    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao excluir venda %s", venda_id)
        raise