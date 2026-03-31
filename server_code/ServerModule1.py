import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

# --- GESTÃO DE UNIDADES ---
@anvil.server.callable
def buscar_unidades():
  unidades = app_tables.unidades.search()
  lista_processada = []
  for u in unidades:
    try:
      total_ativos = len(app_tables.ativos.search(unidade=u))
    except:
      total_ativos = 0
    item = dict(u)
    item['contagem_ativos'] = total_ativos
    item['row_objeto'] = u 
    lista_processada.append(item)
  return lista_processada

# --- GESTÃO DE ATIVOS E FLUIDOS ---
@anvil.server.callable
def buscar_fluidos_lista():
  try:
    nomes = [str(r['nome_fluido']) for r in app_tables.fluidos_referencia.search() if r['nome_fluido']]
    return nomes if nomes else ["Ar Comprimido", "Vapor", "Água"]
  except:
    return ["Ar Comprimido", "Vapor", "Água"]

@anvil.server.callable
def obter_detalhes_fluido(nome_fluido):
  """Busca detalhes usando os nomes reais das colunas: grupo_nr13 e comentario"""
  row = app_tables.fluidos_referencia.get(nome_fluido=nome_fluido)
  if row:
    return {
      'grupo': row['grupo_nr13'], 
      'descricao': row['comentario']
    }
  return None

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes):
  return app_tables.ativos.add_row(**dados_mestre, **especificacoes)

# --- DASHBOARD ---
@anvil.server.callable
def obter_resumo_dashboard():
  hoje = datetime.date.today()
  ativos = app_tables.ativos.search()
  vencidos = sum(1 for a in ativos if a['data_proxima_insp'] and a['data_proxima_insp'] < hoje)
  em_dia = len(ativos) - vencidos
  return {
    'vencidos': vencidos, 'em_dia': em_dia, 
    'total': len(ativos), 'total_unidades': len(app_tables.unidades.search())
  }