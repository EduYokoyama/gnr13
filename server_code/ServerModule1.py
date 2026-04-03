import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import datetime

# --- GESTÃO DE UNIDADES ---

@anvil.server.callable
def buscar_unidades():
  """Busca todas as unidades e conta ativos para o dashboard."""
  unidades = app_tables.unidades.search()
  lista = []
  for u in unidades:
    try:
      total = len(app_tables.ativos.search(unidade=u))
    except:
      total = 0
    lista.append(dict(u, contagem_ativos=total, row_objeto=u))
  return lista

@anvil.server.callable
def salvar_unidade(dados):
  return app_tables.unidades.add_row(**dados)

@anvil.server.callable
def editar_unidade(row, dados):
  if row:
    row.update(**dados)

@anvil.server.callable
def excluir_unidade(row):
  if row:
    row.delete()

# --- GESTÃO DE FLUIDOS ---

@anvil.server.callable
def buscar_fluidos_lista():
  """Busca nomes para popular dropdowns conforme a tabela fluidos_referencia."""
  try:
    return [str(r['nome_fluido']) for r in app_tables.fluidos_referencia.search() if r['nome_fluido']]
  except:
    return ["Ar Comprimido", "Água (Quente ou Fria)", "Vapor de Água"]

@anvil.server.callable
def obter_detalhes_fluido(nome):
  r = app_tables.fluidos_referencia.get(nome_fluido=nome)
  return {'grupo': r['grupo_nr13'], 'descricao': r['comentario']} if r else None

# --- CADASTRO E INVENTÁRIO DE ATIVOS ---

@anvil.server.callable
def obter_specs_ativo(ativo_row):
  """Busca os dados técnicos nas tabelas filhas (Specs) para edição."""
  tipo = ativo_row['tipo']
  if tipo == "Vaso de Pressão":
    return app_tables.specs_vasos.get(ativo=ativo_row)
  elif tipo == "Caldeira":
    return app_tables.specs_caldeiras.get(ativo=ativo_row)
  elif tipo == "Tanque Metálico":
    return app_tables.specs_tanques.get(ativo=ativo_row)
  elif "Tubulação" in tipo:
    return app_tables.specs_tubulacoes.get(ativo=ativo_row)
  return None

@anvil.server.callable
def buscar_ativos_filtrados(unidade=None, tipo=None, status_filtro=None):
  """Busca ativos aplicando filtros e calculando status de cores em tempo real."""
  query = {}
  if unidade: query['unidade'] = unidade
  if tipo and tipo != "Todos": query['tipo'] = tipo

  ativos = app_tables.ativos.search(**query)
  hoje = datetime.date.today()
  lista = []

  for a in ativos:
    dt = a['data_proxima_insp']
    st = "Sem Data"

    # Trava Jurídica: Se não tem prontuário, o status é Cinza (Incompleto)
    if not a['pdf_prontuario']:
      st = "Sem Data"
    elif dt:
      if dt < hoje:
        st = "Vencido"
      elif dt <= hoje + datetime.timedelta(days=30):
        st = "A Vencer (30 dias)"
      else:
        st = "No Prazo"

    if status_filtro and status_filtro != "Todos" and status_filtro != st:
      continue

    lista.append(dict(a, status_inspeção=st, row_objeto=a))
  return lista

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos, item_edicao=None):
  """
    Salva ou Atualiza o ativo e distribui dados pelas tabelas filhas.
    """
  if item_edicao:
    # Modo Edição
    ativo_ref = item_edicao['row_objeto']
    ativo_ref.update(**dados_mestre)

    tipo = dados_mestre['tipo']
    if tipo == "Vaso de Pressão":
      row_spec = app_tables.specs_vasos.get(ativo=ativo_ref)
      if row_spec: row_spec.update(**especificacoes)
      else: app_tables.specs_vasos.add_row(ativo=ativo_ref, **especificacoes)
    elif tipo == "Caldeira":
      row_spec = app_tables.specs_caldeiras.get(ativo=ativo_ref)
      if row_spec: row_spec.update(**especificacoes)
      else: app_tables.specs_caldeiras.add_row(ativo=ativo_ref, **especificacoes)
  else:
    # Modo Novo Cadastro
    ativo_ref = app_tables.ativos.add_row(**dados_mestre)
    tipo = dados_mestre['tipo']
    if tipo == "Vaso de Pressão":
      app_tables.specs_vasos.add_row(ativo=ativo_ref, **especificacoes)
    elif tipo == "Caldeira":
      app_tables.specs_caldeiras.add_row(ativo=ativo_ref, **especificacoes)
    elif tipo == "Tanque Metálico":
      app_tables.specs_tanques.add_row(ativo=ativo_ref, **especificacoes)
    elif "Tubulação" in tipo:
      app_tables.specs_tubulacoes.add_row(ativo=ativo_ref, **especificacoes)

    # Limpa e ressalva instrumentos (Simplificado para o exemplo)
  for inst in app_tables.dispositivos_seguranca.search(ativo=ativo_ref):
    inst.delete()
  if lista_instrumentos:
    for i in lista_instrumentos:
      app_tables.dispositivos_seguranca.add_row(ativo=ativo_ref, **i)

  return ativo_ref

# --- MOTOR DE CÁLCULO NORMATIVO (NR-13 E API 653) ---

@anvil.server.callable
def processar_novo_relatorio(ativo_row, dados_relatorio):
  """
    O 'Cérebro' do Software: Calcula a próxima inspeção com base na Categoria e Escopo.
    """
  # 1. Registra no Histórico (Inclui ART e Relatório conforme solicitado)
  app_tables.historico_inspecoes.add_row(ativo_ref=ativo_row, **dados_relatorio)

  tipo = ativo_row['tipo']
  hoje = datetime.date.today()
  data_base = dados_relatorio['data_inspecao'] or hoje
  escopo = dados_relatorio['escopo']
  apto = dados_relatorio['parecer_conclusivo']

  # Risco Grave e Iminente: Se INAPTO, status Vermelho imediato [1]
  if not apto:
    ativo_row.update(data_proxima_insp=hoje - datetime.timedelta(days=1))
    return "Ativo marcado como INAPTO. Status bloqueado em Vermelho."

  proximo_vencimento = data_base

  # 2. Lógica por Tipo de Ativo
  if tipo == "Vaso de Pressão":
    spec = app_tables.specs_vasos.get(ativo=ativo_row)
    cat = spec['categoria'] if spec else "Categoria V"

    # Prazos Máximos - Tabela 2 NR-13 (Estabelecimentos sem SPIE) [2]
    prazos = {
      "Categoria I":   {"ext": 1, "int": 3},
      "Categoria II":  {"ext": 2, "int": 4},
      "Categoria III": {"ext": 3, "int": 6},
      "Categoria IV":  {"ext": 4, "int": 8},
      "Categoria V":   {"ext": 5, "int": 10}
    }
    regra = prazos.get(cat, prazos["Categoria V"])
    anos = regra["ext"] if escopo == "Exame Externo" else regra["int"]
    proximo_vencimento = data_base + datetime.timedelta(days=anos * 365)

  elif tipo == "Caldeira":
    # Caldeiras A e B (Sem SPIE): 12 meses [3]
    proximo_vencimento = data_base + datetime.timedelta(days=365)

  elif tipo == "Tanque Metálico":
    # API 653: Externo padrão é 5 anos [4]
    proximo_vencimento = data_base + datetime.timedelta(days=5 * 365)

  elif "Tubulação" in tipo:
    # NR-13: Segue o prazo do ativo mais crítico ligado [5]
    proximo_vencimento = data_base + datetime.timedelta(days=2 * 365)

    # 3. Atualiza a data mestre para o Dashboard
  ativo_row.update(data_proxima_insp=proximo_vencimento)

  return f"Inspeção registrada. Próximo vencimento: {proximo_vencimento.strftime('%d/%m/%Y')}"

# --- DASHBOARD ---

@anvil.server.callable
def obter_resumo_dashboard():
  ativos = app_tables.ativos.search()
  hoje = datetime.date.today()
  vencidos = sum(1 for a in ativos if a['data_proxima_insp'] and a['data_proxima_insp'] < hoje)
  return {
    'vencidos': vencidos, 
    'em_dia': len(ativos) - vencidos, 
    'total': len(ativos), 
    'total_unidades': len(app_tables.unidades.search())
  }
