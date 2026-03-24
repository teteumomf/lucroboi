from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.compra import CompraCreate, CompraResponse
from app.domain.services.compra_service import criar_compra
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError

router = APIRouter(prefix="/compras", tags=["Compras"])


@router.post("/", response_model=CompraResponse)
def criar_compra_endpoint(
    payload: CompraCreate,
    usuario = Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        compra, alerta = criar_compra(
            db=db,
            data=payload.data,
            pasto_id=payload.pasto_id,
            quantidade=payload.quantidade,
            valor_total=payload.valor_total,
            usuario=usuario
        )

        response = CompraResponse.from_orm(compra)
        response.alerta_capacidade = alerta

        return response

    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))