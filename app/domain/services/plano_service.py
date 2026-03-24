from app.core.exceptions import DomainError


def validar_limite(
    atual: int,
    limite: int | None,
    mensagem: str,
):
    if limite is None:
        return

    if atual >= limite:
        raise DomainError(mensagem)