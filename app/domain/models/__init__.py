# Importa todos os models em ordem para garantir que o SQLAlchemy
# consiga resolver os relacionamentos entre tabelas corretamente.
# A ordem importa: Plano deve ser importado antes de Usuario.

from app.domain.models.plano import Plano
from app.domain.models.usuario import Usuario
from app.domain.models.conta_bancaria import ContaBancaria
from app.domain.models.pasto import Pasto
from app.domain.models.compra import Compra
from app.domain.models.venda import Venda
from app.domain.models.despesa import Despesa
from app.domain.models.movimentacao_financeira import MovimentacaoFinanceira
from app.domain.models.movimentacao_gado import MovimentacaoGado

__all__ = [
    "Plano",
    "Usuario",
    "ContaBancaria",
    "Pasto",
    "Compra",
    "Venda",
    "Despesa",
    "MovimentacaoFinanceira",
    "MovimentacaoGado",
]
