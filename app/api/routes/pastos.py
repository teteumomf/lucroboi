from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_logado
from app.schemas.pasto import PastoCreate, PastoUpdate, PastoResponse
from app.domain.services import pasto_service
from app.core.exceptions import DomainError

router = APIRouter(prefix="/pastos", tags=["Pastos"])


@router.post("/", response_model=PastoResponse, status_code=201)
def criar(
    payload: PastoCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return pasto_service.criar_pasto(
            db=db,
            nome=payload.nome,
            tamanho_ha=payload.tamanho_ha,
            tipo_pastagem=payload.tipo_pastagem,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[PastoResponse])
def listar(
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return pasto_service.listar_pastos(db=db, usuario=usuario)


@router.get("/{pasto_id}", response_model=PastoResponse)
def detalhe(
    pasto_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return pasto_service.buscar_pasto(db=db, pasto_id=pasto_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{pasto_id}", response_model=PastoResponse)
def editar(
    pasto_id: int,
    payload: PastoUpdate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return pasto_service.editar_pasto(
            db=db,
            pasto_id=pasto_id,
            usuario=usuario,
            nome=payload.nome,
            tamanho_ha=payload.tamanho_ha,
            tipo_pastagem=payload.tipo_pastagem,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{pasto_id}", status_code=204)
def excluir(
    pasto_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        pasto_service.excluir_pasto(db=db, pasto_id=pasto_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
