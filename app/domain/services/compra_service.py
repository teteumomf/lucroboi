from sqlalchemy.orm import Session
from app.domain.models.compra import Compra
from app.domain.models.pasto import Pasto
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
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
            limite=usuario.plano.limite_vendas,
            mensagem="Limite de compras atingido para seu plano",
        )

        if quantidade <= 0:
            raise DomainError("Quantidade deve ser maior que zero")

        if valor_total <= 0:
            raise DomainError("Valor total deve ser maior que zero")

        if isinstance(data, str):
            data = date.fromisoformat(data)

        pasto = db.get(Pasto, pasto_id)

        if not pasto:
            raise DomainError("Pasto não encontrado")

        valor_total_dec = Decimal(str(valor_total))
        frete_dec = Decimal(str(frete))

        custo_total = (valor_total_dec + frete_dec).quantize(Decimal("0.01"))
        valor_unitario = (
                custo_total / Decimal(quantidade)
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

        # Atualiza Pasto
        pasto.quantidade_atual += quantidade
        pasto.custo_total = (
                pasto.custo_total + custo_total
        ).quantize(Decimal("0.01"))

        pasto.custo_medio = (
                pasto.custo_total / Decimal(pasto.quantidade_atual)
        ).quantize(Decimal("0.01"))

        db.add(compra)
        db.commit()
        db.refresh(compra)

        alerta = pasto.quantidade_atual > pasto.capacidade_sugerida

        logger.info("Compra registrada no pasto %s", pasto.id)

        return compra, alerta
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registar compra no pasto")
        raise