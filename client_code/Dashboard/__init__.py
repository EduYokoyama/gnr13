from ._anvil_designer import DashboardTemplate
from anvil import *
import anvil.server

class Dashboard(DashboardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.renderizar_resumo()

  def renderizar_resumo(self):
    resumo = anvil.server.call('obter_resumo_dashboard')

    # Desenhando o gráfico com formato de dicionário para evitar o erro de importação
    self.grafico_status.data = [
      {
        'type': 'pie',
        'labels': ['Em Dia', 'Vencidos/Pendentes'],
        'values': [resumo['em_dia'], resumo['vencidos']],
        'hole': 0.4,
        'marker': {'colors': ['#2ecc71', '#e74c3c']}
      }
    ]

    self.grafico_status.layout.title = f"Resumo: {resumo['total']} Ativos em {resumo['total_unidades']} Unidades"