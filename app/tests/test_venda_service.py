# tests/test_venda_service.py
from app.domain.services.venda_service import criar_venda
from app.domain.services.compra_service import criar_compra
from app.domain.services.pasto_service import criar_pasto
from app.domain.services.conta_service import criar_conta

def test_registrar_venda(db, usuario):
    pasto = criar_pasto(db, "Pasto Venda", 10, "brachiaria", usuario)
    conta = criar_conta(db, "Conta Padrão", 50000, usuario)

    criar_compra(
        db, "2024-01-01", pasto.id, 10, 10000, usuario, conta.id, 500
    )

    venda = criar_venda(
        db=db,
        data="2024-01-10",
        quantidade=5,
        valor_total=7000,
        pasto_id=pasto.id,
        usuario=usuario,
        conta_id=conta.id,
        frete=0.0,
    )

    db.refresh(pasto)

    assert venda.lucro_bruto >= 0
    assert pasto.quantidade_atual == 5