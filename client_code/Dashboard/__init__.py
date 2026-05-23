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
      # 1. Busca os resumos gerais do servidor
      resumo = anvil.server.call('obter_resumo_dashboard')
      
      # Atualiza os painéis numéricos de estatísticas (Value Boxes)
      self.lbl_total_val.text = str(resumo.get('total', 0))
      self.lbl_vencidos_val.text = str(resumo.get('vencidos', 0))
      self.lbl_unidades_val.text = str(resumo.get('total_unidades', 0))
      self.lbl_instrumentos_val.text = str(resumo.get('inst_vencidos', 0))
      
      # 2. Busca lista completa de ativos para o cálculo do cronograma de previsão
      ativos = anvil.server.call('buscar_ativos_filtrados')
      
      # 3. Monta Gráfico 1: Status de Conformidade dos Ativos (Donut Chart)
      self.configurar_grafico_status(resumo)
      
      # 4. Monta Gráfico 2: Status de Calibração dos Instrumentos (Donut Chart)
      self.configurar_grafico_calibracoes(resumo)
      
      # 5. Monta Gráfico 3: Cronograma de Previsão de Inspeções (Timeline Forecast Chart)
      self.configurar_grafico_previsao(ativos)
      
    except Exception as e:
      print(f"Erro ao renderizar dashboard: {e}")
      Notification(f"Erro ao carregar dados do painel: {e}", style="warning").show()

  def configurar_grafico_status(self, resumo):
    # Paleta premium e limpa
    dados = [{
      'type': 'pie',
      'labels': ['Em Dia', 'Vencidos/Pendentes'],
      'values': [resumo['em_dia'], resumo['vencidos']],
      'hole': 0.6,
      'marker': {'colors': ['#10b981', '#ef4444']}, # Verde esmeralda e vermelho coral
      'textinfo': 'percent+value',
      'hoverinfo': 'label+value',
      'textfont': {'family': 'Inter', 'size': 12, 'color': '#1e293b'}
    }]
    
    layout = {
      'title': {
        'text': '<b>Conformidade de Ativos</b>',
        'font': {'family': 'Outfit', 'size': 16, 'color': '#0f172a'}
      },
      'paper_bgcolor': 'rgba(255, 255, 255, 0.65)',
      'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 60, 'b': 20, 'l': 20, 'r': 20},
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': -0.1, 'x': 0.5, 'xanchor': 'center'}
    }
    
    self.plot_status.data = dados
    self.plot_status.layout = layout

  def configurar_grafico_calibracoes(self, resumo):
    inst_vencidos = resumo.get('inst_vencidos', 0)
    inst_total = resumo.get('inst_total', 0)
    inst_em_dia = resumo.get('inst_em_dia', inst_total - inst_vencidos)
    
    dados = [{
      'type': 'pie',
      'labels': ['Calibrados', 'Vencidos'],
      'values': [inst_em_dia, inst_vencidos],
      'hole': 0.6,
      'marker': {'colors': ['#3b82f6', '#f59e0b']}, # Azul moderno e Laranja âmbar
      'textinfo': 'percent+value',
      'hoverinfo': 'label+value',
      'textfont': {'family': 'Inter', 'size': 12, 'color': '#1e293b'}
    }]
    
    layout = {
      'title': {
        'text': '<b>Validação de Instrumentos</b>',
        'font': {'family': 'Outfit', 'size': 16, 'color': '#0f172a'}
      },
      'paper_bgcolor': 'rgba(255, 255, 255, 0.65)',
      'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 60, 'b': 20, 'l': 20, 'r': 20},
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': -0.1, 'x': 0.5, 'xanchor': 'center'}
    }
    
    self.plot_calibrations.data = dados
    self.plot_calibrations.layout = layout

  def configurar_grafico_previsao(self, ativos):
    # 1. Gera os próximos 12 meses (incluindo o atual)
    hoje = datetime.date.today()
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    meses_futuros = []
    cronograma_counts = []
    
    ano_corrente = hoje.year
    mes_corrente = hoje.month
    
    for i in range(12):
      m = mes_corrente + i
      a = ano_corrente + (m - 1) // 12
      m = (m - 1) % 12 + 1
      meses_futuros.append((a, m, f"{meses_nomes[m-1]}/{str(a)[2:]}"))
      cronograma_counts.append(0)
      
    # 2. Distribui os ativos no cronograma
    for a in ativos:
      dt = a.get('data_proxima_insp')
      if dt:
        # Se for string (o Anvil às vezes converte em string ISO em transportes remotos), tratamos
        if isinstance(dt, str):
          try:
            dt = datetime.datetime.strptime(dt[:10], "%Y-%m-%d").date()
          except:
            continue
        
        # Filtra apenas inspeções futuras (ou dentro do período de 12 meses)
        for idx, (ano_f, mes_f, label) in enumerate(meses_futuros):
          if dt.year == ano_f and dt.month == mes_f:
            cronograma_counts[idx] += 1
            break
            
    # 3. Plota o gráfico (Timeline Forecast Chart)
    x_labels = [label for _, _, label in meses_futuros]
    y_values = cronograma_counts
    
    dados = [{
      'x': x_labels,
      'y': y_values,
      'type': 'bar',
      'name': 'Inspeções Agendadas',
      'marker': {
        'color': '#3b82f6',
        'opacity': 0.85,
        'line': {'color': '#1d4ed8', 'width': 1.5}
      }
    }, {
      'x': x_labels,
      'y': y_values,
      'type': 'scatter',
      'mode': 'lines+markers',
      'name': 'Tendência',
      'line': {'color': '#10b981', 'width': 3, 'shape': 'spline'},
      'marker': {'size': 8, 'color': '#10b981'}
    }]
    
    layout = {
      'title': {
        'text': '<b>Cronograma e Previsão de Próximas Inspeções (12 Meses)</b>',
        'font': {'family': 'Outfit', 'size': 18, 'color': '#0f172a'}
      },
      'paper_bgcolor': 'rgba(0,0,0,0)',
      'plot_bgcolor': 'rgba(0,0,0,0)',
      'margin': {'t': 70, 'b': 50, 'l': 55, 'r': 35},
      'xaxis': {
        'gridcolor': 'rgba(148, 163, 184, 0.1)',
        'tickfont': {'family': 'Inter', 'size': 11, 'color': '#475569'}
      },
      'yaxis': {
        'gridcolor': 'rgba(148, 163, 184, 0.15)',
        'tickfont': {'family': 'Inter', 'size': 11, 'color': '#475569'},
        'title': {'text': 'Qtd. Equipamentos', 'font': {'family': 'Inter', 'size': 12}}
      },
      'showlegend': True,
      'legend': {'orientation': 'h', 'y': 1.1, 'x': 0.5, 'xanchor': 'center'}
    }
    
    self.plot_forecast.data = dados
    self.plot_forecast.layout = layout