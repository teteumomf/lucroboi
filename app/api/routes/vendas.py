from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_logado
from app.schemas.venda import VendaCreate, VendaResponse
from app.domain.services import venda_service
from app.core.exceptions import DomainError

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("/", response_model=VendaResponse, status_code=201)
def criar(
    payload: VendaCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return venda_service.criar_venda(
            db=db,
            data=payload.data,
            pasto_id=payload.pasto_id,
            quantidade=payload.quantidade,
            valor_total=payload.valor_total,
            usuario=usuario,
            conta_id=payload.conta_id,
            frete=payload.frete or 0.0,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[VendaResponse])
def listar(
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return venda_service.listar_vendas(db=db, usuario=usuario)


@router.get("/{venda_id}", response_model=VendaResponse)
def detalhe(
    venda_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return venda_service.buscar_venda(db=db, venda_id=venda_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{venda_id}", status_code=204)
def excluir(
    venda_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        venda_service.excluir_venda(db=db, venda_id=venda_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
