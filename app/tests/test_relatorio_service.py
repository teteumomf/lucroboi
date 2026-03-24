# tests/test_relatorio_service.py
from app.domain.services.relatorio_service import resumo_geral

def test_resumo_geral(db, usuario):
    resultado = resumo_geral(db, usuario)

    assert "total_animais" in resultado
    assert "saldo_caixa" in resultado