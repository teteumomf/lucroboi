from app.core.database import SessionLocal
from app.domain.models.plano import Plano

db = SessionLocal()

planos = [
    Plano(
        nome="Gratis",
        limite_contas=1,
        limite_pastos=3,
        limite_vendas=3,
        limite_compras=3,
        limite_despesas=3,
        limite_movimentacoes=3,
        relatorio_resumo=True,
        relatorio_por_pasto=False,
        relatorio_fluxo_caixa=False,
        relatorio_dre=False,
        relatorio_evolucao_patrimonio=False,
        relatorio_resultado_mensal=False,
        relatorio_giro_animais=False,
        relatorio_ranking_pastos=False,
    ),
    Plano(
        nome="Basico",
        limite_contas=3,
        limite_pastos=10,
        limite_vendas=15,
        limite_compras=15,
        limite_despesas=15,
        limite_movimentacoes=10,
        relatorio_resumo=True,
        relatorio_por_pasto=True,
        relatorio_fluxo_caixa=False,
        relatorio_dre=False,
        relatorio_evolucao_patrimonio=False,
        relatorio_resultado_mensal=True,
        relatorio_giro_animais=False,
        relatorio_ranking_pastos=True,
    ),
    Plano(
        nome="Completo",
        limite_contas=None,
        limite_pastos=None,
        limite_vendas=None,
        limite_compras=None,
        limite_despesas=None,
        limite_movimentacoes=None,
        relatorio_resumo=True,
        relatorio_por_pasto=True,
        relatorio_fluxo_caixa=True,
        relatorio_dre=True,
        relatorio_evolucao_patrimonio=True,
        relatorio_resultado_mensal=True,
        relatorio_giro_animais=True,
        relatorio_ranking_pastos=True,
    ),
]

for plano in planos:
    if not db.query(Plano).filter(Plano.nome == plano.nome).first():
        db.add(plano)

db.commit()
db.close()