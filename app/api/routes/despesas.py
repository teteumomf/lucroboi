from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.despesa import DespesaCreate, DespesaResponse
from app.domain.services.despesa_service import criar_despesa
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError
router = APIRouter(prefix="/despesas", tags=["Despesas"])


@router.post("/", response_model=DespesaResponse)
def criar_despesa_endpoint(
    payload: DespesaCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return criar_despesa(
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