from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.venda import VendaCreate, VendaResponse
from app.domain.services.venda_service import criar_venda
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("/", response_model=VendaResponse)
def criar_venda_endpoint(
    payload: VendaCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return criar_venda(
            db=db,
            data=payload.data,
            pasto_id=payload.pasto_id,
            quantidade=payload.quantidade,
            valor_total=payload.valor_total,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))