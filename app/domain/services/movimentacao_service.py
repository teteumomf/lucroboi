from sqlalchemy.orm import Session
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.models.conta_bancaria import ContaBancaria
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario
from app.domain.services.plano_service import validar_limite
from decimal import Decimal


def registrar_movimentacao(
    db: Session,
    data,
    tipo: str,
    descricao: str,
    valor: float,
    conta_id: int,
    usuario: Usuario,
    compra_id: int | None = None,
    venda_id: int | None = None,
    despesa_id: int | None = None,
) -> MovimentacaoFinanceira:
    """
    Adiciona movimentação à sessão SEM commitar.
    O commit é responsabilidade do service chamador.
    """
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

    valor_dec = Decimal(str(valor))

    if tipo == "entrada":
        conta.saldo = (Decimal(str(conta.saldo)) + valor_dec).quantize(Decimal("0.01"))
    elif tipo in ("saida", "despesa"):
        conta.saldo = (Decimal(str(conta.saldo)) - valor_dec).quantize(Decimal("0.01"))
    else:
        raise DomainError("Tipo de movimentação inválido")

    movimentacao = MovimentacaoFinanceira(
        data=data,
        tipo=tipo,
        descricao=descricao,
        valor=valor,
        conta_id=conta_id,
        usuario_id=usuario.id,
        compra_id=compra_id,
        venda_id=venda_id,
        despesa_id=despesa_id,
    )

    db.add(movimentacao)
    logger.info(
        "Movimentação adicionada à sessão (compra_id=%s, venda_id=%s, despesa_id=%s)",
        compra_id, venda_id, despesa_id,
    )
    return movimentacao