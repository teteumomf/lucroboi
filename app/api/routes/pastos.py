from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.pasto import PastoCreate, PastoResponse
from app.domain.services.pasto_service import criar_pasto
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError

router = APIRouter(prefix="/pastos", tags=["Pastos"])


@router.post("/", response_model=PastoResponse)
def criar(
    payload: PastoCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return criar_pasto(
            db=db,
            nome=payload.nome,
            tamanho_ha=payload.tamanho_ha,
            tipo_pastagem=payload.tipo_pastagem,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))