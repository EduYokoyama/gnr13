import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

# ==============================================================================
# 1. GESTÃO DE UNIDADES (PLANTAS)
# ==============================================================================

@anvil.server.callable
def buscar_unidades():
  """Retorna unidades processadas com a contagem real de ativos"""
  unidades = app_tables.unidades.search()
  lista_processada = []

  for u in unidades:
    try:
      # Conta ativos vinculados a esta unidade 'u'
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
  """Adiciona uma nova unidade"""
  return app_tables.unidades.add_row(
    nome_unidade=dados['nome'],
    endereco_unidade=dados['endereco'],
    cidade=dados['cidade'],
    estado=dados['estado'],
    cep=dados['cep'],
    telefone=dados['telefone'],
    lat_long=dados['lat_long']
  )

@anvil.server.callable
def editar_unidade(row, dados):
  """Atualiza uma unidade existente"""
  row.update(
    nome_unidade=dados['nome'],
    endereco_unidade=dados['endereco'],
    cidade=dados['cidade'],
    estado=dados['estado'],
    cep=dados['cep'],
    telefone=dados['telefone'],
    lat_long=dados['lat_long']
  )

@anvil.server.callable
def excluir_unidade(row):
  """Remove a unidade do banco de dados"""
  row.delete()

# ==============================================================================
# 2. GESTÃO DE ATIVOS (EQUIPAMENTOS NR-13)
# ==============================================================================

@anvil.server.callable
def buscar_fluidos_lista():
  """Busca os nomes dos fluidos da tabela de referência para o DropDown"""
  try:
    # Tenta buscar da sua tabela 'fluidos_referencia'
    return [r['nome_fluido'] for r in app_tables.fluidos_referencia.search()]
  except:
    # Se a tabela não existir ou falhar, retorna uma lista padrão
    return ["Ar Comprimido", "Vapor", "Água", "GLP", "Nitrogênio", "Outros"]

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes):
  """Salva o ativo unindo dados básicos e especificações técnicas"""
  return app_tables.ativos.add_row(**dados_mestre, **especificacoes)

# ==============================================================================
# 3. DASHBOARD E INDICADORES
# ==============================================================================

@anvil.server.callable
def obter_resumo_dashboard():
  """Calcula indicadores para o gráfico de rosca baseado em data_proxima_insp"""
  hoje = datetime.date.today()
  ativos = app_tables.ativos.search()
  unidades = app_tables.unidades.search()

  vencidos = 0
  em_dia = 0

  for a in ativos:
    data_insp = a['data_proxima_insp']

    if data_insp:
      if data_insp < hoje:
        vencidos += 1
      else:
        em_dia += 1
    else:
      # Se não tem data, contamos como 'Em Dia' para evitar erro no gráfico
      em_dia += 1

  return {
    'vencidos': vencidos,
    'em_dia': em_dia,
    'total': len(ativos),
    'total_unidades': len(unidades)
  }