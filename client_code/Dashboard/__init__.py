from ._anvil_designer import DashboardTemplate
from anvil import *
import anvil.server
import datetime

class Dashboard(DashboardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.renderizar_dashboard()

  def renderizar_dashboard(self):
    try:
      # 1. Busca resumo geral
      resumo = anvil.server.call('obter_resumo_dashboard')

      # Atualiza value boxes
      self.lbl_total_val.text = str(resumo.get('total', 0))
      self.lbl_vencidos_val.text = str(resumo.get('vencidos', 0))
      self.lbl_unidades_val.text = str(resumo.get('total_unidades', 0))
      self.lbl_instrumentos_val.text = str(resumo.get('inst_vencidos', 0))

      # 2. Busca ativos e instrumentos
      ativos = anvil.server.call('buscar_ativos_filtrados')
      instrumentos = anvil.server.call('buscar_instrumentos_filtrados')

      # 3. Gráficos pizza (donut)
      self.configurar_grafico_status(resumo)
      self.configurar_grafico_calibracoes(resumo)

      # 4. Gráficos de previsão
      self.configurar_grafico_previsao(ativos)
      self.configurar_grafico_previsao_instrumentos(instrumentos)

    except Exception as e:
      print(f"Erro ao renderizar dashboard: {e}")
      Notification(f"Erro ao carregar dados do painel: {e}", style="warning").show()

  # ── Donut: Ativos ──────────────────────────────────────────────────────────
  def configurar_grafico_status(self, resumo):
    dados = [{
      'type': 'pie',
      'labels': ['Em Dia', 'Vencidos/Pendentes'],
      'values': [resumo['em_dia'], resumo['vencidos']],
      'hole': 0.6,
      'marker': {'colors': ['#10b981', '#ef4444']},
      'textinfo': 'percent+value',
      'hoverinfo': 'label+value',
      'textfont': {'family': 'Inter', 'size': 12, 'color': '#1e293b'}
    }]
    layout = {
      'title': {'text': '<b>Conformidade de Ativos</b>', 'font': {'family': 'Outfit', 'size': 16, 'color': '#0f172a'}},
      'paper_bgcolor': 'rgba(255,255,255,0.65)',
      'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 60, 'b': 20, 'l': 20, 'r': 20},
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': -0.1, 'x': 0.5, 'xanchor': 'center'}
    }
    self.plot_status.data = dados
    self.plot_status.layout = layout

  # ── Donut: Instrumentos ────────────────────────────────────────────────────
  def configurar_grafico_calibracoes(self, resumo):
    inst_vencidos = resumo.get('inst_vencidos', 0)
    inst_total = resumo.get('inst_total', 0)
    inst_em_dia = resumo.get('inst_em_dia', inst_total - inst_vencidos)
    dados = [{
      'type': 'pie',
      'labels': ['Calibrados', 'Vencidos'],
      'values': [inst_em_dia, inst_vencidos],
      'hole': 0.6,
      'marker': {'colors': ['#3b82f6', '#f59e0b']},
      'textinfo': 'percent+value',
      'hoverinfo': 'label+value',
      'textfont': {'family': 'Inter', 'size': 12, 'color': '#1e293b'}
    }]
    layout = {
      'title': {'text': '<b>Validação de Instrumentos</b>', 'font': {'family': 'Outfit', 'size': 16, 'color': '#0f172a'}},
      'paper_bgcolor': 'rgba(255,255,255,0.65)',
      'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 60, 'b': 20, 'l': 20, 'r': 20},
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': -0.1, 'x': 0.5, 'xanchor': 'center'}
    }
    self.plot_calibrations.data = dados
    self.plot_calibrations.layout = layout

  # ── Helper: gera lista de meses futuros ───────────────────────────────────
  def _gerar_meses(self, meses):
    hoje = datetime.date.today()
    nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    resultado = []
    for i in range(meses):
      m = hoje.month + i
      a = hoje.year + (m - 1) // 12
      m = (m - 1) % 12 + 1
      resultado.append((a, m, f"{nomes[m-1]}/{str(a)[2:]}"))
    return resultado

  def _contar_por_mes(self, itens, campo_data, meses_futuros):
    counts = [0] * len(meses_futuros)
    for item in itens:
      dt = item.get(campo_data)
      if dt:
        if isinstance(dt, str):
          try:
            dt = datetime.datetime.strptime(dt[:10], "%Y-%m-%d").date()
          except:
            continue
        for idx, (ano_f, mes_f, _) in enumerate(meses_futuros):
          if dt.year == ano_f and dt.month == mes_f:
            counts[idx] += 1
            break
    return counts

  # ── Forecast: Ativos ───────────────────────────────────────────────────────
  def configurar_grafico_previsao(self, ativos):
    botoes = []
    meses_opcoes = [12, 24, 36]
    default_mes = 12
    
    meses_12 = self._gerar_meses(12)
    counts_12 = self._contar_por_mes(ativos, 'data_proxima_insp', meses_12)
    labels_12 = [l for _, _, l in meses_12]

    for m in meses_opcoes:
      meses_futuros = self._gerar_meses(m)
      counts = self._contar_por_mes(ativos, 'data_proxima_insp', meses_futuros)
      x_labels = [l for _, _, l in meses_futuros]
      
      botoes.append({
        'method': 'update',
        'label': f'{m} Meses',
        'args': [
           {'x': [x_labels, x_labels], 'y': [counts, counts]}, 
           {'title.text': f'<b>Cronograma de Inspeções ({m} Meses)</b>'}
        ]
      })

    dados = [{
      'x': labels_12, 'y': counts_12, 'type': 'bar',
      'name': 'Inspeções Agendadas',
      'marker': {'color': '#3b82f6', 'opacity': 0.85, 'line': {'color': '#1d4ed8', 'width': 1.5}}
    }, {
      'x': labels_12, 'y': counts_12, 'type': 'scatter',
      'mode': 'lines+markers', 'name': 'Tendência',
      'line': {'color': '#10b981', 'width': 3, 'shape': 'spline'},
      'marker': {'size': 8, 'color': '#10b981'}
    }]
    
    layout = {
      'title': {'text': f'<b>Cronograma de Inspeções ({default_mes} Meses)</b>', 'font': {'family': 'Outfit', 'size': 16, 'color': '#0f172a'}},
      'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 70, 'b': 50, 'l': 55, 'r': 35},
      'xaxis': {'gridcolor': 'rgba(148,163,184,0.1)', 'tickfont': {'family': 'Inter', 'size': 11, 'color': '#475569'}},
      'yaxis': {'gridcolor': 'rgba(148,163,184,0.15)', 'tickfont': {'family': 'Inter', 'size': 11, 'color': '#475569'},
                'title': {'text': 'Qtd. Equipamentos', 'font': {'family': 'Inter', 'size': 12}}},
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': -0.2, 'x': 0.5, 'xanchor': 'center'},
      'updatemenus': [{
          'buttons': botoes,
          'direction': 'down',
          'showactive': True,
          'x': 1.0,
          'xanchor': 'right',
          'y': 1.15,
          'yanchor': 'top',
          'bgcolor': '#f8fafc',
          'bordercolor': '#cbd5e1'
      }]
    }
    self.plot_forecast_ativos.data = dados
    self.plot_forecast_ativos.layout = layout

  # ── Forecast: Instrumentos ─────────────────────────────────────────────────
  def configurar_grafico_previsao_instrumentos(self, instrumentos):
    botoes = []
    meses_opcoes = [12, 24, 36]
    default_mes = 12
    
    meses_12 = self._gerar_meses(12)
    counts_12 = self._contar_por_mes(instrumentos, 'prazo_calibracao', meses_12)
    labels_12 = [l for _, _, l in meses_12]

    for m in meses_opcoes:
      meses_futuros = self._gerar_meses(m)
      counts = self._contar_por_mes(instrumentos, 'prazo_calibracao', meses_futuros)
      x_labels = [l for _, _, l in meses_futuros]
      
      botoes.append({
        'method': 'update',
        'label': f'{m} Meses',
        'args': [
           {'x': [x_labels, x_labels], 'y': [counts, counts]}, 
           {'title.text': f'<b>Previsão de Calibrações ({m} Meses)</b>'}
        ]
      })

    dados = [{
      'x': labels_12, 'y': counts_12, 'type': 'bar',
      'name': 'Calibrações Agendadas',
      'marker': {'color': '#f59e0b', 'opacity': 0.85, 'line': {'color': '#b45309', 'width': 1.5}}
    }, {
      'x': labels_12, 'y': counts_12, 'type': 'scatter',
      'mode': 'lines+markers', 'name': 'Tendência',
      'line': {'color': '#3b82f6', 'width': 3, 'shape': 'spline'},
      'marker': {'size': 8, 'color': '#3b82f6'}
    }]
    
    layout = {
      'title': {'text': f'<b>Previsão de Calibrações ({default_mes} Meses)</b>', 'font': {'family': 'Outfit', 'size': 16, 'color': '#0f172a'}},
      'paper_bgcolor': 'rgba(0,0,0,0)', 'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 70, 'b': 50, 'l': 55, 'r': 35},
      'xaxis': {'gridcolor': 'rgba(148,163,184,0.1)', 'tickfont': {'family': 'Inter', 'size': 11, 'color': '#475569'}},
      'yaxis': {'gridcolor': 'rgba(148,163,184,0.15)', 'tickfont': {'family': 'Inter', 'size': 11, 'color': '#475569'},
                'title': {'text': 'Qtd. Instrumentos', 'font': {'family': 'Inter', 'size': 12}}},
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': -0.2, 'x': 0.5, 'xanchor': 'center'},
      'updatemenus': [{
          'buttons': botoes,
          'direction': 'down',
          'showactive': True,
          'x': 1.0,
          'xanchor': 'right',
          'y': 1.15,
          'yanchor': 'top',
          'bgcolor': '#f8fafc',
          'bordercolor': '#cbd5e1'
      }]
    }
    self.plot_forecast_instrumentos.data = dados
    self.plot_forecast_instrumentos.layout = layout
