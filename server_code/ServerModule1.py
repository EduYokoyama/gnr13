import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

@anvil.server.callable
def buscar_unidades():
  return app_tables.unidades.search()

@anvil.server.callable
def salvar_unidade(dados):
  """Salva a unidade no banco de dados com a estrutura completa"""
  return app_tables.unidades.add_row(
    nome_unidade=dados['nome'],
    endereco_unidade=dados['endereco'],
    cidade=dados['cidade'],
    estado=dados['estado'],
    cep=dados['cep'],
    telefone=dados['telefone'],
    lat_long=dados.get('lat_long', '')
  )

@anvil.server.callable
def atualizar_unidade(row, novo_nome):
  row['nome_unidade'] = novo_nome

@anvil.server.callable
def excluir_unidade(row):
  row.delete()

@anvil.server.callable
def obter_resumo_dashboard():
  import datetime
  hoje = datetime.date.today()
  ativos = app_tables.ativos.search()
  vencidos = 0
  em_dia = 0
  for a in ativos:
    if a['data_proxima_insp'] and a['data_proxima_insp'] < hoje:
      vencidos += 1
    else:
      em_dia += 1
  return {
    'vencidos': vencidos, 
    'em_dia': em_dia, 
    'total': len(ativos),
    'total_unidades': len(app_tables.unidades.search())
  }