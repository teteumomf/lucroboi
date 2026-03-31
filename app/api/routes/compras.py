from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_logado
from app.schemas.compra import CompraCreate, CompraResponse
from app.domain.services import compra_service
from app.core.exceptions import DomainError

router = APIRouter(prefix="/compras", tags=["Compras"])


@router.post("/", response_model=CompraResponse, status_code=201)
def criar(
    payload: CompraCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        compra, alerta = compra_service.criar_compra(
            db=db,
            data=payload.data,
            pasto_id=payload.pasto_id,
            quantidade=payload.quantidade,
            valor_total=payload.valor_total,
            usuario=usuario,
            conta_id=payload.conta_id,
            frete=payload.frete or 0.0,
        )
        response = CompraResponse.model_validate(compra)
        response.alerta_capacidade = alerta
        return response
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[CompraResponse])
def listar(
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    return compra_service.listar_compras(db=db, usuario=usuario)


@router.get("/{compra_id}", response_model=CompraResponse)
def detalhe(
    compra_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return compra_service.buscar_compra(db=db, compra_id=compra_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{compra_id}", status_code=204)
def excluir(
    compra_id: int,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        compra_service.excluir_compra(db=db, compra_id=compra_id, usuario=usuario)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
