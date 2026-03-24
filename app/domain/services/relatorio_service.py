from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.domain.models.pasto import Pasto
from app.domain.models.venda import Venda
from app.domain.models.conta_bancaria import ContaBancaria
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.models.despesa import Despesa

from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger
from app.domain.models.usuario import Usuario


def resumo_geral(db: Session, usuario: Usuario):
    try:
        if not usuario.plano.relatorio_resumo:
            raise DomainError(
                "Seu plano não permite relatório de resumo geral"
            )

        total_animais = db.query(
            func.sum(Pasto.quantidade_atual)
        ).filter(
            Pasto.usuario_id == usuario.id
        ).scalar() or 0

        custo_total = db.query(
            func.sum(Pasto.custo_total)
        ).filter(
            Pasto.usuario_id == usuario.id
        ).scalar() or 0

        receita_total = db.query(
            func.sum(Venda.valor_total)
        ).filter(
            Venda.usuario_id == usuario.id
        ).scalar() or 0

        lucro_total = db.query(
            func.sum(Venda.lucro_bruto)
        ).filter(
            Venda.usuario_id == usuario.id
        ).scalar() or 0

        saldo_caixa = db.query(
            func.sum(ContaBancaria.saldo)
        ).filter(
            ContaBancaria.usuario_id == usuario.id
        ).scalar() or 0

        logger.info("Relatório de resumo geral gerado com sucesso")
        return {
            "total_animais": total_animais,
            "custo_total": float(custo_total),
            "receita_total": float(receita_total),
            "lucro_total": float(lucro_total),
            "saldo_caixa": float(saldo_caixa),
        }
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao gerar relatório de resumo geral")
        raise

def resultado_por_pasto(db: Session, usuario: Usuario):
    try:
        if not usuario.plano.relatorio_por_pasto:
            raise DomainError(
                "Seu plano não permite relatório por pasto"
            )
        resultados = (
            db.query(
                Pasto.id,
                Pasto.nome,
                Pasto.quantidade_atual,
                Pasto.custo_medio,
                Pasto.custo_total,
                func.coalesce(func.sum(Venda.valor_total), 0).label("receita"),
                func.coalesce(func.sum(Venda.lucro_bruto), 0).label("lucro"),
            )
            .outerjoin(Venda, Venda.pasto_id == Pasto.id)
            .filter(Pasto.usuario_id == usuario.id)
            .group_by(Pasto.id)
            .all()
        )
        logger.info("Relatório de resultado por pasto gerado com sucesso")
        return [
            {
                "pasto_id": r.id,
                "pasto": r.nome,
                "quantidade": r.quantidade_atual,
                "custo_medio": float(r.custo_medio),
                "custo_total": float(r.custo_total),
                "receita": float(r.receita),
                "lucro": float(r.lucro),
            }
            for r in resultados
        ]
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao gerar relatório de resultado por pasto")
        raise

def fluxo_caixa(
    db: Session,
    data_inicio: date,
    data_fim: date,
    usuario: Usuario
):
    try:
        if not usuario.plano.relatorio_fluxo_caixa:
            raise DomainError(
                "Seu plano não permite relatório de fluxo de caixa"
            )
        entradas = (
            db.query(func.sum(MovimentacaoFinanceira.valor))
            .filter(
                MovimentacaoFinanceira.tipo == "entrada",
                MovimentacaoFinanceira.data.between(data_inicio, data_fim),
                MovimentacaoFinanceira.usuario_id == usuario.id,
            )
            .scalar()
            or 0
        )

        saidas = (
            db.query(func.sum(MovimentacaoFinanceira.valor))
            .filter(
                MovimentacaoFinanceira.tipo == "saida",
                MovimentacaoFinanceira.data.between(data_inicio, data_fim),
                MovimentacaoFinanceira.usuario_id == usuario.id,
            )
            .scalar()
            or 0
        )
        logger.info("Relatório de fluxo de caixa gerado com sucesso")
        return {
            "periodo_inicio": data_inicio,
            "periodo_fim": data_fim,
            "entradas": float(entradas),
            "saidas": float(saidas),
            "resultado": float(entradas - saidas),
        }
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao gerar relatório de fluxo de caixa")
        raise

def dre_simples(
    db: Session,
    data_inicio: date,
    data_fim: date,
    usuario: Usuario
):
    try:
        if not usuario.plano.relatorio_dre:
            raise DomainError(
                "Seu plano não permite relatório de DRE"
            )

        receita = (
            db.query(func.sum(Venda.valor_total))
            .filter(Venda.data.between(data_inicio, data_fim), Venda.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        custo_vendas = (
            db.query(func.sum(Venda.custo_total))
            .filter(Venda.data.between(data_inicio, data_fim), Venda.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        despesas = (
            db.query(func.sum(Despesa.valor))
            .filter(Despesa.data.between(data_inicio, data_fim), Despesa.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        lucro_bruto = receita - custo_vendas
        resultado = lucro_bruto - despesas
        logger.info("Relatório de DRE gerado com sucesso")
        return {
            "periodo_inicio": data_inicio,
            "periodo_fim": data_fim,
            "receita": float(receita),
            "custo_vendas": float(custo_vendas),
            "lucro_bruto": float(lucro_bruto),
            "despesas": float(despesas),
            "resultado": float(resultado),
        }
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao gerar relatório de DRE")
        raise


def evolucao_patrimonio(db: Session, usuario: Usuario):
    try:
        if not usuario.plano.relatorio_evolucao_patrimonio:
            raise DomainError(
                "Seu plano não permite relatório de evolução de patrimônio"
            )
        # pode ficar disponível no Básico
        saldo_caixa = (
            db.query(func.sum(ContaBancaria.saldo))
            .filter(ContaBancaria.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        valor_gado = (
            db.query(func.sum(Pasto.custo_total))
            .filter(Pasto.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        patrimonio = saldo_caixa + valor_gado

        logger.info("Relatório de evolução do patrimônio gerado")
        return {
            "saldo_caixa": float(saldo_caixa),
            "valor_gado": float(valor_gado),
            "patrimonio_total": float(patrimonio),
        }

    except SQLAlchemyError:
        logger.error("Erro ao gerar relatório de patrimônio")
        raise

def resultado_mensal(db: Session, usuario: Usuario):
    try:
        if not usuario.plano.relatorio_resultado_mensal:
            raise DomainError(
                "Seu plano não permite relatório de resultado mensal"
            )
        resultados = (
            db.query(
                func.year(Venda.data).label("ano"),
                func.month(Venda.data).label("mes"),
                func.sum(Venda.valor_total).label("receita"),
                func.sum(Venda.lucro_bruto).label("lucro"),
            )
            .filter(Venda.usuario_id == usuario.id)
            .group_by("ano", "mes")
            .order_by("ano", "mes")
            .all()
        )

        logger.info("Relatório de resultado mensal gerado")
        return [
            {
                "ano": r.ano,
                "mes": r.mes,
                "receita": float(r.receita or 0),
                "lucro": float(r.lucro or 0),
            }
            for r in resultados
        ]

    except SQLAlchemyError:
        logger.error("Erro ao gerar relatório mensal")
        raise

def giro_animais(db: Session, usuario: Usuario):
    try:
        if not usuario.plano.relatorio_giro_animais:
            raise DomainError(
                "Seu plano não permite relatório de giro de animais"
            )

        total_comprados = (
            db.query(func.sum(Pasto.quantidade_atual))
            .filter(Pasto.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        total_vendidos = (
            db.query(func.sum(Venda.quantidade))
            .filter(Venda.usuario_id == usuario.id)
            .scalar()
            or 0
        )

        estoque_atual = total_comprados - total_vendidos
        giro = (
            total_vendidos / total_comprados
            if total_comprados > 0 else 0
        )

        logger.info("Relatório de giro de animais gerado")
        return {
            "total_comprados": int(total_comprados),
            "total_vendidos": int(total_vendidos),
            "estoque_atual": int(estoque_atual),
            "taxa_giro": round(giro, 2),
        }

    except SQLAlchemyError:
        logger.error("Erro ao gerar relatório de giro")
        raise

def ranking_pastos(db: Session, usuario: Usuario):

    if not usuario.plano.relatorio_ranking_pastos:
        raise DomainError(
            "Seu plano não permite relatório de ranking de pastos"
        )

    resultados = (
        db.query(
            Pasto.nome,
            func.coalesce(func.sum(Venda.lucro_bruto), 0).label("lucro"),
        )
        .join(Venda, Venda.pasto_id == Pasto.id)
        .filter(Pasto.usuario_id == usuario.id)
        .group_by(Pasto.id)
        .order_by(func.sum(Venda.lucro_bruto).desc())
        .all()
    )

    return [
        {
            "pasto": r.nome,
            "lucro": float(r.lucro),
        }
        for r in resultados
    ]