import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime

# --- GESTÃO DE UNIDADES ---
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

# --- GESTÃO DE FLUIDOS ---
@anvil.server.callable
def buscar_fluidos_lista():
  try: return [str(r['nome_fluido']) for r in app_tables.fluidos_referencia.search()]
  except: return ["Ar", "Água"]

@anvil.server.callable
def obter_detalhes_fluido(nome):
  r = app_tables.fluidos_referencia.get(nome_fluido=nome)
  return {'grupo': r['grupo_nr13'], 'descricao': r['comentario']} if r else None

# --- GESTÃO DE ATIVOS (NR-13) ---
@anvil.server.callable
def buscar_ativos_filtrados(unidade=None, tipo=None, status_filtro=None):
  query = {}
  if unidade: query['unidade'] = unidade
  if tipo and tipo != "Todos": query['tipo'] = tipo
  ativos = app_tables.ativos.search(**query)
  hoje = datetime.date.today()
  lista = []
  for a in ativos:
    dt = a['data_proxima_insp']
    st = "Sem Data"
    if dt:
      st = "Vencido" if dt < hoje else ("A Vencer (30 dias)" if dt <= hoje + datetime.timedelta(days=30) else "No Prazo")
    if status_filtro and status_filtro != "Todos" and status_filtro != st: continue
    lista.append(dict(a, status_inspeção=st, row_objeto=a))
  return lista

@anvil.server.callable
def obter_specs_ativo(row_ativo):
  tipo = row_ativo['tipo']
  if tipo == "Vaso de Pressão":
    r = app_tables.specs_vasos.get(ativo=row_ativo)
    return dict(r) if r else {}
  elif tipo == "Caldeira":
    r = app_tables.specs_caldeiras.get(ativo=row_ativo)
    return dict(r) if r else {}
  elif tipo == "Tanque Metálico":
    r = app_tables.specs_tanques.get(ativo=row_ativo)
    return dict(r) if r else {}
  elif "Tubulação" in tipo or "Sistemas" in tipo:
    r = app_tables.specs_tubulacoes.get(ativo=row_ativo)
    return dict(r) if r else {}
  return {}

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos, row_existente=None):
  # 1. Atualização Tabela Ativos (Mestre) com proteção
  try:
    if row_existente:
      row_existente.update(**dados_mestre)
      ativo_ref = row_existente
    else:
      ativo_ref = app_tables.ativos.add_row(**dados_mestre)
  except Exception as e:
    if 'ano_prontuario' in dados_mestre:
      print("Aviso Anvil: Coluna 'ano_prontuario' com divergência. Salvando mestre sem este campo.")
      del dados_mestre['ano_prontuario']
      if row_existente:
        row_existente.update(**dados_mestre)
        ativo_ref = row_existente
      else:
        ativo_ref = app_tables.ativos.add_row(**dados_mestre)
    else:
      raise e

  tipo = dados_mestre.get('tipo', '')

  # 2. Direcionamento para Especificações Corretas
  tabelas = {
    "Vaso de Pressão": app_tables.specs_vasos,
    "Caldeira": app_tables.specs_caldeiras,
    "Tanque Metálico": app_tables.specs_tanques,
    "Sistemas de Tubulação": app_tables.specs_tubulacoes,
    "Tubulação": app_tables.specs_tubulacoes
  }

  if tipo in tabelas:
    tabela = tabelas[tipo]
    row_spec = tabela.get(ativo=ativo_ref)
    if row_spec:
      row_spec.update(**especificacoes)
    else:
      tabela.add_row(ativo=ativo_ref, **especificacoes)

  # 3. Atualização de Instrumentos de Segurança
  if row_existente:
    for r in app_tables.dispositivos_seguranca.search(ativo=ativo_ref):
      r.delete()

  if lista_instrumentos:
    for i in lista_instrumentos:
      app_tables.dispositivos_seguranca.add_row(ativo=ativo_ref, **i)

  return ativo_ref

@anvil.server.callable
def excluir_ativo_completo(row_ativo):
  # Remove dependências primeiro para não quebrar a integridade
  for spec_table in [app_tables.specs_vasos, app_tables.specs_caldeiras, app_tables.specs_tanques, app_tables.specs_tubulacoes]:
    for r in spec_table.search(ativo=row_ativo):
      r.delete()
  for r in app_tables.dispositivos_seguranca.search(ativo=row_ativo):
    r.delete()
  # Remove o mestre
  row_ativo.delete()

# --- DASHBOARD ---
@anvil.server.callable
def obter_resumo_dashboard():
  ativos = app_tables.ativos.search()
  hoje = datetime.date.today()
  vencidos = sum(1 for a in ativos if a['data_proxima_insp'] is not None and a['data_proxima_insp'] < hoje)
  return {'vencidos': vencidos, 'em_dia': len(ativos) - vencidos, 'total': len(ativos), 'total_unidades': len(app_tables.unidades.search())}

@anvil.server.callable
def buscar_ativos_pais():
  """Retorna os ativos principais que podem ser interligados a uma tubulação"""
  # Buscamos apenas os equipamentos que geram ou acumulam pressão
  return app_tables.ativos.search(tipo=q.any_of("Vaso de Pressão", "Caldeira", "Tanque Metálico"))

@anvil.server.callable
def buscar_ativos_grid(texto_busca=""):
  """Filtra os ativos no banco de dados para a tela de Pop-up de seleção"""
  if texto_busca:
    # Busca por TAGs que contenham o texto digitado (ilike ignora maiúsculas/minúsculas)
    return app_tables.ativos.search(
      tipo=q.any_of("Vaso de Pressão", "Caldeira", "Tanque Metálico"),
      tag=q.ilike(f"%{texto_busca}%")
    )
  else:
    # Se não digitou nada, retorna todos os pais possíveis
    return app_tables.ativos.search(tipo=q.any_of("Vaso de Pressão", "Caldeira", "Tanque Metálico"))