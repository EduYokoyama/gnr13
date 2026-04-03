from ._anvil_designer import DashboardTemplate
from anvil import *
import anvil.server

class Dashboard(DashboardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.renderizar_resumo()

  def renderizar_resumo(self):
    resumo = anvil.server.call('obter_resumo_dashboard')

    # Dicionário puro - o Python básico do Anvil lê sem problemas
    dados_grafico = [
      {
        'type': 'pie',
        'labels': ['Em Dia', 'Vencidos/Pendentes'],
        'values': [resumo['em_dia'], resumo['vencidos']],
        'hole': 0.4,
        'marker': {'colors': ['#2ecc71', '#e74c3c']}
      }
    ]
    titulo = f"Resumo: {resumo['total']} Ativos em {resumo['total_unidades']} Unidades"

    # Envia para o gráfico, não importa o nome que ele tenha ficado no seu Design
    if hasattr(self, 'plot_1'):
      self.plot_1.data = dados_grafico
      self.plot_1.layout.title = titulo
    elif hasattr(self, 'grafico_status'):
      self.grafico_status.data = dados_grafico
      self.grafico_status.layout.title = titulo