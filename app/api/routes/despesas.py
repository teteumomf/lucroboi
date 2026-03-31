from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_logado
from app.schemas.despesa import DespesaCreate, DespesaResponse
from app.domain.services import despesa_service
from app.core.exceptions import DomainError

router = APIRouter(prefix="/despesas", tags=["Despesas"])


@router.post("/", response_model=DespesaResponse, status_code=201)
def criar(
    payload: DespesaCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return despesa_service.criar_despesa(
            db=db,
            data=payload.data,
            descricao=payload.descricao,
            valor=payload.valor,
            pasto_id=payload.pasto_id,
            conta_id=payload.conta_id,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[DespesaResponse])
def listar(
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return despesa_service.listar_despesas(db=db, usuario=usuario)


@router.get("/{despesa_id}", response_model=DespesaResponse)
def detalhe(
    despesa_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return despesa_service.buscar_despesa(db=db, despesa_id=despesa_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{despesa_id}", status_code=204)
def excluir(
    despesa_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        despesa_service.excluir_despesa(db=db, despesa_id=despesa_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
