from ._anvil_designer import DashboardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import plotly.graph_objects as go

class Dashboard(DashboardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.renderizar_resumo()

  def renderizar_resumo(self):
    resumo = anvil.server.call('obter_resumo_dashboard')

    # Atualiza gráfico
    self.grafico_status.data = [
      go.Pie(
        labels=['Em Dia', 'Vencidos/Pendentes'],
        values=[resumo['em_dia'], resumo['vencidos']],
        hole=.4,
        marker=dict(colors=['#2ecc71', '#e74c3c'])
      )
    ]

    # Título dinâmico com total de unidades
    self.grafico_status.layout.title = (
      f"Resumo: {resumo['total']} Ativos em {resumo['total_unidades']} Unidades"
    )