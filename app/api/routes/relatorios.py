from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_db
from app.domain.services import relatorio_service
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.get("/resumo-geral")
def resumo(usuario=Depends(get_usuario_logado), db: Session = Depends(get_db)):
    return relatorio_service.resumo_geral(db, usuario)


@router.get("/por-pasto")
def por_pasto(usuario=Depends(get_usuario_logado), db: Session = Depends(get_db)):
    return relatorio_service.resultado_por_pasto(db, usuario)


@router.get("/fluxo-caixa")
def fluxo(
    data_inicio: date,
    data_fim: date,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return relatorio_service.fluxo_caixa(db, data_inicio, data_fim, usuario)


@router.get("/dre")
def dre(
    data_inicio: date,
    data_fim: date,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return relatorio_service.dre_simples(db, data_inicio, data_fim, usuario)

@router.get("/patrimonio")
def relatorio_patrimonio(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    return relatorio_service.evolucao_patrimonio(db, usuario)

@router.get("/resultado-mensal")
def relatorio_resultado_mensal(
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado),
):
    return relatorio_service.resultado_mensal(db, usuario)

@router.get("/giro-animais")
def relatorio_giro_animais(
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado),
):
    return relatorio_service.giro_animais(db, usuario)

@router.get("/ranking-pastos")
def relatorio_ranking_pastos(
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado),
):
    return relatorio_service.ranking_pastos(db, usuario)