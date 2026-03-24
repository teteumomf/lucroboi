from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.usuario import (
    UsuarioCreate, UsuarioLogin, TokenResponse
)
from app.domain.services.usuario_service import (
    criar_usuario, autenticar_usuario
)
from app.core.exceptions import DomainError

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register")
def register(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
):
    try:
        return criar_usuario(
            db=db,
            nome=payload.nome,
            email=payload.email,
            senha=payload.senha,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UsuarioLogin,
    db: Session = Depends(get_db),
):
    try:
        token = autenticar_usuario(
            db=db,
            email=payload.email,
            senha=payload.senha,
        )
        return {"access_token": token}
    except DomainError as e:
        raise HTTPException(status_code=401, detail=str(e))