from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.financeiro import (
    ContaCreate, ContaResponse
)
from app.domain.services.conta_service import criar_conta
from app.api.deps import get_usuario_logado
from app.core.exceptions import DomainError

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


@router.post("/contas", response_model=ContaResponse)
def criar_conta_endpoint(
    payload: ContaCreate,
    usuario=Depends(get_usuario_logado),
    db: Session = Depends(get_db),
):
    try:
        return criar_conta(
            db=db,
            nome=payload.nome,
            saldo_inicial=payload.saldo_inicial,
            usuario=usuario,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))