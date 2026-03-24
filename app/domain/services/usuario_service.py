from sqlalchemy.orm import Session
from app.domain.models.usuario import Usuario
from app.core.security import gerar_hash_senha, verificar_senha
from app.core.auth import criar_token
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import DomainError
from app.core.logging import logger

def criar_usuario(
    db: Session,
    nome: str,
    email: str,
    senha: str,
):
    try:
        if db.query(Usuario).filter(Usuario.email == email).first():
            raise DomainError("E-mail já cadastrado")

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=gerar_hash_senha(senha),
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        logger.info("Usuario registrado: %s", usuario.nome)
        return usuario
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao registrar usuário")
        raise


def autenticar_usuario(
    db: Session,
    email: str,
    senha: str,
):
    try:
        usuario = db.query(Usuario).filter(
            Usuario.email == email,
            Usuario.ativo == True,
        ).first()

        if not usuario or not verificar_senha(senha, usuario.senha_hash):
            raise DomainError("Credenciais inválidas")

        token = criar_token({"sub": str(usuario.id)})
        logger.info("Autenticação de usuário registrada")
        return token
    except SQLAlchemyError:
        db.rollback()
        logger.info("Erro ao autenticar usuário: %s", usuario.email)
        raise