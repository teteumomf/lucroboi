from sqlalchemy.orm import Session
from app.domain.models.movimentacao_gado import MovimentacaoGado
from app.domain.models.pasto import Pasto
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
from decimal import Decimal

def mover_gado(
    db: Session,
    data,
    pasto_origem_id: int,
    pasto_destino_id: int,
    quantidade: int,
    usuario: Usuario
):
    try:

        total_movimentacoes = db.query(MovimentacaoGado).filter(
            MovimentacaoGado.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_movimentacoes,
            limite=usuario.plano.limite_movimentacoes,
            mensagem="Limite de movimentações de gado atingido para seu plano",
        )

        if pasto_origem_id == pasto_destino_id:
            raise DomainError("Pasto de origem e destino não podem ser o mesmo")

        if quantidade <= 0:
            raise DomainError("Quantidade deve ser maior que zero")

        origem = db.get(Pasto, pasto_origem_id)
        destino = db.get(Pasto, pasto_destino_id)

        if not origem or not destino:
            raise DomainError("Pasto de origem ou destino não encontrado")

        if quantidade > origem.quantidade_atual:
            raise DomainError("Quantidade maior que o disponível no pasto de origem")

        custo_unitario = Decimal(origem.custo_medio)
        custo_transferido = (custo_unitario * Decimal(quantidade)).quantize(Decimal("0.01"))

        # Atualiza origem
        origem.quantidade_atual -= quantidade
        origem.custo_total = (
                origem.custo_total - custo_transferido
        ).quantize(Decimal("0.01"))

        if origem.quantidade_atual > 0:
            origem.custo_medio = (
                    origem.custo_total / Decimal(origem.quantidade_atual)
            ).quantize(Decimal("0.01"))
        else:
            origem.custo_medio = 0
            origem.custo_total = 0

        # Atualiza destino
        destino.quantidade_atual += quantidade
        destino.custo_total = (
                destino.custo_total + custo_transferido
        ).quantize(Decimal("0.01"))

        destino.custo_medio = (
                destino.custo_total / Decimal(destino.quantidade_atual)
        ).quantize(Decimal("0.01"))

        movimentacao = MovimentacaoGado(
            data=data,
            pasto_origem_id=pasto_origem_id,
            pasto_destino_id=pasto_destino_id,
            quantidade=quantidade,
            custo_unitario=float(custo_unitario),
            usuario_id=usuario.id,
        )

        db.add(movimentacao)
        db.commit()
        db.refresh(movimentacao)
        logger.info("Movimentação de gado registrada")
        return movimentacao
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registrar movimentação de gado")
        raise