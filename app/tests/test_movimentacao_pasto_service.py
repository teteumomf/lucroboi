# tests/test_movimentacao_pasto_service.py
from app.domain.services.movimentacao_gado_service import mover_gado
from app.domain.services.pasto_service import criar_pasto
from app.domain.services.compra_service import criar_compra
from app.domain.services.conta_service import criar_conta
from datetime import date

def test_movimentacao_entre_pastos(db, usuario):
    origem = criar_pasto(db, "Origem", 10, "brachiaria", usuario)
    destino = criar_pasto(db, "Destino", 10, "brachiaria", usuario)
    conta = criar_conta(db, "Conta Padrão", 50000, usuario)
    criar_compra(db, "2024-01-01", origem.id, 10, 10000, usuario, conta.id)
    data = "2024-01-01"
    if isinstance(data, str):
        data = date.fromisoformat(data)

    mover_gado(
        db=db,
        data=data,
        pasto_origem_id=origem.id,
        pasto_destino_id=destino.id,
        quantidade=4,
        usuario=usuario
    )

    db.refresh(origem)
    db.refresh(destino)

    assert origem.quantidade_atual == 6
    assert destino.quantidade_atual == 4