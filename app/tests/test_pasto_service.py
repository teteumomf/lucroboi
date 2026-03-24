# tests/test_pasto_service.py
from app.domain.services.pasto_service import criar_pasto

def test_criar_pasto(db, usuario):
    pasto = criar_pasto(
        db=db,
        nome="Pasto A",
        tamanho_ha=10,
        tipo_pastagem="brachiaria",
        usuario=usuario
    )

    assert pasto.id is not None
    assert pasto.nome == "Pasto A"
    assert pasto.quantidade_atual == 0