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
    try: total = len(app_tables.ativos.search(unidade=u))
    except: total = 0
    lista.append(dict(u, contagem_ativos=total, row_objeto=u))
  return lista

@anvil.server.callable
def salvar_unidade(dados):
  return app_tables.unidades.add_row(**dados)

@anvil.server.callable
def editar_unidade(row, dados):
  if row: row.update(**dados)

@anvil.server.callable
def excluir_unidade(row):
  if row: row.delete()

@anvil.server.callable
def buscar_fluidos_lista():
  try: return [str(r['nome_fluido']) for r in app_tables.fluidos_referencia.search()]
  except: return ["Ar", "Água"]

@anvil.server.callable
def obter_detalhes_fluido(nome):
  r = app_tables.fluidos_referencia.get(nome_fluido=nome)
  return {'grupo': r['grupo_nr13'], 'descricao': r['comentario']} if r else None

@anvil.server.callable
def buscar_ativos_filtrados(unidade=None, tipo=None, status_filtro=None):
  query = {}
  if unidade: query['unidade'] = unidade
  if tipo and tipo != "Todos": query['tipo'] = tipo
  ativos = app_tables.ativos.search(**query)
  hoje = datetime.date.today()
  lista = []
  for a in ativos:
    dt = a.get('data_proxima_insp')
    st = "Sem Data"
    if dt:
      st = "Vencido" if dt < hoje else ("A Vencer (30 dias)" if dt <= hoje + datetime.timedelta(days=30) else "No Prazo")
    if status_filtro and status_filtro != "Todos" and status_filtro != st: continue
    lista.append(dict(a, status_inspeção=st, row_objeto=a))
  return lista

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos, row_existente=None):
  ativo_ref = app_tables.ativos.add_row(**dados_mestre)
  tipo = dados_mestre['tipo']
  if tipo == "Vaso de Pressão": app_tables.specs_vasos.add_row(ativo=ativo_ref, **especificacoes)
  elif "Tubulação" in tipo: app_tables.specs_tubulacoes.add_row(ativo=ativo_ref, **especificacoes)
  if lista_instrumentos:
    for i in lista_instrumentos: app_tables.dispositivos_seguranca.add_row(ativo=ativo_ref, **i)
  return ativo_ref

@anvil.server.callable
def obter_resumo_dashboard():
  ativos = app_tables.ativos.search()
  hoje = datetime.date.today()
  vencidos = sum(1 for a in ativos if a.get('data_proxima_insp') and a['data_proxima_insp'] < hoje)
  return {'vencidos': vencidos, 'em_dia': len(ativos) - vencidos, 'total': len(ativos), 'total_unidades': len(app_tables.unidades.search())}