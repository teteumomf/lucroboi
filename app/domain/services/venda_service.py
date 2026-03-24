from sqlalchemy.orm import Session
from app.domain.models.venda import Venda
from app.domain.models.pasto import Pasto
from app.domain.services.movimentacao_service import registrar_movimentacao
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
from app.domain.models.conta_bancaria import ContaBancaria
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
            ContaBancaria.usuario_id == usuario.id
        ).first()

        if not conta:
            raise DomainError("Conta bancária não encontrada")

        if conta.saldo < (valor_total - frete):
            raise DomainError("Saldo insuficiente na conta")

        if quantidade <= 0:
            raise DomainError("Quantidade deve ser maior que zero")

        if valor_total <= 0:
            raise DomainError("Valor total deve ser maior que zero")

        if isinstance(data, str):
            data = date.fromisoformat(data)

        pasto = db.get(Pasto, pasto_id)

        if not pasto:
            raise DomainError("Pasto não encontrado")

        if quantidade > pasto.quantidade_atual:
            raise DomainError("Quantidade maior que o estoque disponível no pasto")

        valor_total_d = Decimal(str(valor_total))
        frete_d = Decimal(str(frete))
        quantidade_d = Decimal(quantidade)

        valor_unitario = (valor_total_d / quantidade_d).quantize(Decimal("0.01"))
        custo_unitario = Decimal(pasto.custo_medio)
        custo_total = (custo_unitario * quantidade_d).quantize(Decimal("0.01"))

        lucro_bruto = (
                valor_total_d - custo_total - frete_d
        ).quantize(Decimal("0.01"))

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

        # Atualiza Pasto
        pasto.quantidade_atual -= quantidade
        pasto.custo_total = (
                pasto.custo_total - custo_total
        ).quantize(Decimal("0.01"))

        if pasto.quantidade_atual > 0:
            pasto.custo_medio = round(
                pasto.custo_total / pasto.quantidade_atual, 2
            )
        else:
            pasto.custo_medio = 0
            pasto.custo_total = 0

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
        logger.info("Erro ao registrar venda")
        raise