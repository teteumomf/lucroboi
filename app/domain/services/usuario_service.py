from sqlalchemy.orm import Session
from app.domain.models.usuario import Usuario
from app.domain.models.plano import Plano
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

        # Busca o plano Grátis automaticamente para novos cadastros
        plano_gratis = db.query(Plano).filter(Plano.nome == "Gratis").first()

        if not plano_gratis:
            raise DomainError(
                "Plano padrão não encontrado. "
                "Execute o seed de planos antes de cadastrar usuários: "
                "python -m app.scripts.seed_planos"
            )

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=gerar_hash_senha(senha),
            plano_id=plano_gratis.id,
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        logger.info("Usuário registrado: %s (plano: %s)", usuario.nome, plano_gratis.nome)
        return usuario
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao registrar usuário")
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
        logger.info("Usuário autenticado: %s", usuario.id)
        return token
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao autenticar usuário")
        raise


def trocar_senha(
    db: Session,
    usuario: Usuario,
    senha_atual: str,
    nova_senha: str,
) -> None:
    try:
        if not verificar_senha(senha_atual, usuario.senha_hash):
            raise DomainError("Senha atual incorreta")

        if len(nova_senha) < 6:
            raise DomainError("A nova senha deve ter pelo menos 6 caracteres")

        usuario.senha_hash = gerar_hash_senha(nova_senha)
        db.commit()
        logger.info("Senha alterada para usuário: %s", usuario.id)
    except SQLAlchemyError:
        db.rollback()
        logger.error("Erro ao trocar senha do usuário %s", usuario.id)
        raise