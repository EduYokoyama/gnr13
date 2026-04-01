import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

@anvil.server.callable
def buscar_unidades():
  unidades = app_tables.unidades.search()
  lista = []
  for u in unidades:
    try:
      total = len(app_tables.ativos.search(unidade=u))
    except:
      total = 0
    item = dict(u)
    item['contagem_ativos'] = total
    item['row_objeto'] = u 
    lista.append(item)
  return lista

@anvil.server.callable
def buscar_fluidos_lista():
  try:
    return [str(r['nome_fluido']) for r in app_tables.fluidos_referencia.search()]
  except:
    return ["Ar Comprimido", "Vapor", "Água"]

@anvil.server.callable
def obter_detalhes_fluido(nome_fluido):
  row = app_tables.fluidos_referencia.get(nome_fluido=nome_fluido)
  if row:
    return {'grupo': row['grupo_nr13'], 'descricao': row['comentario']}
  return None

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos=None):
  # 1. Salva Ativo
  novo_ativo = app_tables.ativos.add_row(**dados_mestre, **especificacoes)
  # 2. Salva Dispositivos na tabela correta
  if lista_instrumentos:
    for inst in lista_instrumentos:
      app_tables.dispositivos_seguranca.add_row(
        ativo=novo_ativo,
        tag_instrumento=inst.get('tag'),
        tipo=inst.get('tipo'),
        num_serie=inst.get('serie'),
        ano_fabricacao=inst.get('ano_fab'),
        data_calibracao=inst.get('data_cal'),
        prazo_calibracao=inst.get('prazo'),
        status=inst.get('status')
      )
  return novo_ativo

@anvil.server.callable
def obter_resumo_dashboard():
  hoje = datetime.date.today()
  ativos = app_tables.ativos.search()
  vencidos = sum(1 for a in ativos if a['data_proxima_insp'] and a['data_proxima_insp'] < hoje)
  return {'vencidos': vencidos, 'em_dia': len(ativos) - vencidos, 'total': len(ativos), 'total_unidades': len(app_tables.unidades.search())}