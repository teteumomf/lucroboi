from sqlalchemy.orm import Session
from app.domain.models.pasto import Pasto
from app.domain.models.compra import Compra
from app.domain.models.venda import Venda
from app.domain.models.despesa import Despesa
from app.domain.models.enums import TipoPastagem
from app.domain.models.usuario import Usuario
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.services.plano_service import validar_limite

TAXA_LOTACAO = {
    TipoPastagem.BRACHIARIA: 1.2,
    TipoPastagem.MOMBACA: 3.0,
    TipoPastagem.TANZANIA: 2.5,
}


def calcular_capacidade(tamanho_ha: float, tipo_pastagem: TipoPastagem) -> int:
    taxa = TAXA_LOTACAO.get(tipo_pastagem, 1)
    return int(tamanho_ha * taxa)


def criar_pasto(
    db: Session,
    nome: str,
    tamanho_ha: float,
    tipo_pastagem: TipoPastagem,
    usuario: Usuario,
) -> Pasto:
    try:
        total_pastos = db.query(Pasto).filter(
            Pasto.usuario_id == usuario.id
        ).count()

        validar_limite(
            atual=total_pastos,
            limite=usuario.plano.limite_pastos,
            mensagem="Limite de pastos atingido para seu plano",
        )

        if tamanho_ha <= 0:
            raise DomainError("Tamanho do pasto deve ser maior que zero")

        capacidade = calcular_capacidade(tamanho_ha=tamanho_ha, tipo_pastagem=tipo_pastagem)

        pasto = Pasto(
            nome=nome,
            tamanho_ha=tamanho_ha,
            tipo_pastagem=tipo_pastagem,
            capacidade_sugerida=capacidade,
            quantidade_atual=0,
            custo_total=0,
            custo_medio=0,
            status="ativo",
            usuario_id=usuario.id,
        )

        db.add(pasto)
        db.commit()
        db.refresh(pasto)
        logger.info("Pasto registrado: %s", pasto.id)
        return pasto
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao registrar pasto")
        raise


def listar_pastos(db: Session, usuario: Usuario) -> list[Pasto]:
    return (
        db.query(Pasto)
        .filter(Pasto.usuario_id == usuario.id)
        .order_by(Pasto.nome)
        .all()
    )


def buscar_pasto(db: Session, pasto_id: int, usuario: Usuario) -> Pasto:
    pasto = db.query(Pasto).filter(
        Pasto.id == pasto_id,
        Pasto.usuario_id == usuario.id,
    ).first()

    if not pasto:
        raise DomainError("Pasto não encontrado")

    return pasto


def editar_pasto(
    db: Session,
    pasto_id: int,
    usuario: Usuario,
    nome: str | None = None,
    tamanho_ha: float | None = None,
    tipo_pastagem: TipoPastagem | None = None,
) -> Pasto:
    try:
        pasto = buscar_pasto(db, pasto_id, usuario)

        if nome is not None:
            pasto.nome = nome

        if tamanho_ha is not None:
            if tamanho_ha <= 0:
                raise DomainError("Tamanho do pasto deve ser maior que zero")
            pasto.tamanho_ha = tamanho_ha

        # Recalcula capacidade se tamanho ou tipo mudou
        if tamanho_ha is not None or tipo_pastagem is not None:
            tipo_final = tipo_pastagem if tipo_pastagem is not None else pasto.tipo_pastagem
            tamanho_final = tamanho_ha if tamanho_ha is not None else float(pasto.tamanho_ha)
            pasto.tipo_pastagem = tipo_final
            pasto.capacidade_sugerida = calcular_capacidade(tamanho_final, tipo_final)

        db.commit()
        db.refresh(pasto)
        logger.info("Pasto editado: %s", pasto.id)
        return pasto
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao editar pasto")
        raise


def excluir_pasto(db: Session, pasto_id: int, usuario: Usuario) -> None:
    try:
        pasto = buscar_pasto(db, pasto_id, usuario)

        if pasto.quantidade_atual > 0:
            raise DomainError(
                f"Não é possível excluir o pasto '{pasto.nome}' pois há "
                f"{pasto.quantidade_atual} animal(is) alocado(s). "
                "Mova ou venda os animais antes de excluir."
            )

        # Bloqueia se houver histórico vinculado
        tem_compras = db.query(Compra).filter(Compra.pasto_id == pasto_id).first()
        if tem_compras:
            raise DomainError(
                f"Não é possível excluir o pasto '{pasto.nome}' pois existem "
                "compras vinculadas a ele. Exclua as compras antes de excluir o pasto."
            )

        tem_vendas = db.query(Venda).filter(Venda.pasto_id == pasto_id).first()
        if tem_vendas:
            raise DomainError(
                f"Não é possível excluir o pasto '{pasto.nome}' pois existem "
                "vendas vinculadas a ele. Exclua as vendas antes de excluir o pasto."
            )

        tem_despesas = db.query(Despesa).filter(Despesa.pasto_id == pasto_id).first()
        if tem_despesas:
            raise DomainError(
                f"Não é possível excluir o pasto '{pasto.nome}' pois existem "
                "despesas vinculadas a ele. Exclua as despesas antes de excluir o pasto."
            )

        db.delete(pasto)
        db.commit()
        logger.info("Pasto excluído: %s", pasto_id)
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao excluir pasto")
        raise
