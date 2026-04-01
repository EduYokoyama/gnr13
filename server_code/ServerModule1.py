import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

# ==============================================================================
# GESTÃO DE UNIDADES (ATUALIZADO COM CONTAGEM REAL)
# ==============================================================================
@anvil.server.callable
def buscar_unidades():
  """Busca unidades e calcula quantos ativos cada uma possui"""
  unidades = app_tables.unidades.search()
  lista_processada = []

  for u in unidades:
    try:
      # Conta quantos ativos estão vinculados a esta linha de unidade específica
      total_ativos = len(app_tables.ativos.search(unidade=u))
    except:
      total_ativos = 0

      # Criamos um dicionário para o cliente, incluindo o objeto da linha (row_objeto)
    item = dict(u)
    item['contagem_ativos'] = total_ativos
    item['row_objeto'] = u 
    lista_processada.append(item)

  return lista_processada

@anvil.server.callable
def salvar_unidade(dados):
  """Cria uma nova unidade"""
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
  """Atualiza uma unidade existente"""
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
  """Remove a unidade do banco"""
  if row_unidade and row_unidade.is_valid():
    row_unidade.delete()

# ==============================================================================
# GESTÃO DE FLUIDOS E DASHBOARD PRINCIPAL
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
def obter_resumo_dashboard():
  hoje = datetime.date.today()
  ativos = app_tables.ativos.search()
  vencidos = 0
  for a in ativos:
    try:
      if a['data_proxima_insp'] and a['data_proxima_insp'] < hoje:
        vencidos += 1
    except:
      pass
  return {
    'vencidos': vencidos, 
    'em_dia': len(ativos) - vencidos, 
    'total': len(ativos), 
    'total_unidades': len(app_tables.unidades.search())
  }

# ==============================================================================
# SALVAMENTO DE ATIVOS
# ==============================================================================
@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos=None):
  novo_ativo = app_tables.ativos.add_row(**dados_mestre)
  tipo_eq = dados_mestre['tipo']

  if tipo_eq == "Vaso de Pressão":
    app_tables.specs_vasos.add_row(ativo=novo_ativo, **especificacoes)
  elif any(x in tipo_eq for x in ["Tubulação", "Sistemas de Tubulação"]):
    app_tables.specs_tubulacoes.add_row(ativo=novo_ativo, **especificacoes)

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