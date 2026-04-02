import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

# ==============================================================================
# GESTÃO DE UNIDADES (COM CONTAGEM REAL)
# ==============================================================================
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

@anvil.server.callable
def salvar_unidade(dados):
  return app_tables.unidades.add_row(
    nome_unidade=dados['nome'],
    cidade=dados['cidade'],
    estado=dados['estado'],
    endereco_unidade=dados['endereco'],
    cep=dados['cep'],
    telefone=dados['telefone'],
    lat_long=dados['lat_long']
  )

@anvil.server.callable
def editar_unidade(row_unidade, dados):
  if row_unidade and row_unidade.is_valid():
    row_unidade.update(
      nome_unidade=dados['nome'],
      cidade=dados['cidade'],
      estado=dados['estado'],
      endereco_unidade=dados['endereco'],
      cep=dados['cep'],
      telefone=dados['telefone'],
      lat_long=dados['lat_long']
    )

@anvil.server.callable
def excluir_unidade(row_unidade):
  if row_unidade and row_unidade.is_valid():
    row_unidade.delete()

# ==============================================================================
# GESTÃO DE FLUIDOS E BUSCA FILTRADA DE ATIVOS
# ==============================================================================
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
def buscar_ativos_filtrados(unidade=None, tipo=None, status_filtro=None):
  query = {}
  if unidade: query['unidade'] = unidade
  if tipo and tipo != "Todos": query['tipo'] = tipo

  ativos = app_tables.ativos.search(**query)
  hoje = datetime.date.today()
  prazo_30 = hoje + datetime.timedelta(days=30)

  lista_final = []
  for a in ativos:
    dt = a.get('data_proxima_insp')
    status = "Sem Data"
    if dt:
      if dt < hoje: status = "Vencido"
      elif dt <= prazo_30: status = "A Vencer (30 dias)"
      else: status = "No Prazo"

    if status_filtro and status_filtro != "Todos" and status_filtro != status:
      continue

    item = dict(a)
    item['status_inspeção'] = status
    item['row_objeto'] = a
    lista_final.append(item)
  return lista_final

# ==============================================================================
# SALVAMENTO E ATUALIZAÇÃO DE ATIVOS
# ==============================================================================
@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos=None, row_existente=None):
  if row_existente:
    row_existente.update(**dados_mestre)
    ativo_ref = row_existente
    # Limpa dependências para regravar na edição
    for r in app_tables.dispositivos_seguranca.search(ativo=ativo_ref): r.delete()
    for r in app_tables.specs_vasos.search(ativo=ativo_ref): r.delete()
    for r in app_tables.specs_tubulacoes.search(ativo=ativo_ref): r.delete()
  else:
    ativo_ref = app_tables.ativos.add_row(**dados_mestre)

  tipo_eq = dados_mestre['tipo']
  if tipo_eq == "Vaso de Pressão":
    app_tables.specs_vasos.add_row(ativo=ativo_ref, **especificacoes)
  elif any(x in tipo_eq for x in ["Tubulação", "Sistemas de Tubulação"]):
    app_tables.specs_tubulacoes.add_row(ativo=ativo_ref, **especificacoes)

  if lista_instrumentos:
    for inst in lista_instrumentos:
      app_tables.dispositivos_seguranca.add_row(ativo=ativo_ref, **inst)
  return ativo_ref

@anvil.server.callable
def obter_resumo_dashboard():
  hoje = datetime.date.today()
  ativos = app_tables.ativos.search()
  vencidos = 0
  for a in ativos:
    try:
      if a['data_proxima_insp'] and a['data_proxima_insp'] < hoje:
        vencidos += 1
    except: pass
  return {
    'vencidos': vencidos, 
    'em_dia': len(ativos) - vencidos, 
    'total': len(ativos), 
    'total_unidades': len(app_tables.unidades.search())
  }