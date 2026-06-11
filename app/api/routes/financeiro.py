from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_logado
from app.schemas.financeiro import ContaCreate, ContaUpdate, ContaResponse
from app.domain.services import conta_service
from app.core.exceptions import DomainError

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


@router.post("/contas", response_model=ContaResponse, status_code=201)
def criar_conta(
    payload: ContaCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return conta_service.criar_conta(
            db=db,
            nome=payload.nome,
            saldo_inicial=payload.saldo_inicial,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contas", response_model=list[ContaResponse])
def listar_contas(
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return conta_service.listar_contas(db=db, usuario=usuario)


@router.get("/contas/{conta_id}", response_model=ContaResponse)
def detalhe_conta(
    conta_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return conta_service.buscar_conta(db=db, conta_id=conta_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/contas/{conta_id}", response_model=ContaResponse)
def editar_conta(
    conta_id: int,
    payload: ContaUpdate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return conta_service.editar_conta(
            db=db,
            conta_id=conta_id,
            usuario=usuario,
            nome=payload.nome,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/contas/{conta_id}", status_code=204)
def excluir_conta(
    conta_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        conta_service.excluir_conta(db=db, conta_id=conta_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
