from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.movimentacao_gado import (
    MovimentacaoGadoCreate,
    MovimentacaoGadoResponse,
)
from app.domain.services.movimentacao_gado_service import mover_gado
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError

router = APIRouter(
    prefix="/movimentacoes-gado",
    tags=["Movimentação de Gado"]
)


@router.post("/", response_model=MovimentacaoGadoResponse)
def mover_gado_endpoint(
    payload: MovimentacaoGadoCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return mover_gado(
            db=db,
            data=payload.data,
            pasto_origem_id=payload.pasto_origem_id,
            pasto_destino_id=payload.pasto_destino_id,
            quantidade=payload.quantidade,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))