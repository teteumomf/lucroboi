# tests/test_compra_service.py
from app.domain.services.compra_service import criar_compra
from app.domain.services.pasto_service import criar_pasto
from app.domain.services.conta_service import criar_conta

def test_registrar_compra(db, usuario):
    pasto = criar_pasto(
        db, "Pasto Compra", 10, "brachiaria", usuario
    )

    conta = criar_conta(db, "Conta Padrão", 50000, usuario)

    compra, alerta = criar_compra(
        db=db,
        data="2024-01-01",
        quantidade=10,
        valor_total=10000,
        frete=500,
        pasto_id=pasto.id,
        conta_id=conta.id,
        usuario=usuario
    )

    db.refresh(pasto)

    assert compra.id is not None
    assert pasto.quantidade_atual == 10
    assert pasto.custo_total > 0