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
def salvar_ativo_completo(dados_mestre, especificacoes, lista_instrumentos=None, row_existente=None):
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

  # --- O QUE MUDOU: ---
  # Removemos completamente o bloco 3 (Atualização de Instrumentos).
  # Agora os instrumentos são salvos/editados nas suas próprias funções exclusivas, 
  # evitando que o histórico seja apagado por engano ao editar um ativo mestre.

  # O retorno da linha (row) é vital para o pop-up abrir corretamente
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
  # Resumo de Equipamentos Principais
  vencidos = sum(1 for a in ativos if a['data_proxima_insp'] is not None and a['data_proxima_insp'] < hoje)

  # Resumo Exclusivo de Instrumentos (Ignora os "Substituídos")
  instrumentos_ativos = app_tables.dispositivos_seguranca.search(status="Ativo")
  inst_vencidos = sum(1 for i in instrumentos_ativos if i['prazo_calibracao'] is not None and i['prazo_calibracao'] < hoje)

  return {
    'vencidos': vencidos, 
    'em_dia': len(ativos) - vencidos, 
    'total': len(ativos), 
    'total_unidades': len(app_tables.unidades.search()),
    'inst_vencidos': inst_vencidos,
    'inst_em_dia': len(instrumentos_ativos) - inst_vencidos,
    'inst_total': len(instrumentos_ativos)
  }
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

@anvil.server.callable
def processar_novo_relatorio(row_ativo, dados_relatorio):
  """
  Salva o novo relatório no histórico e atualiza as datas de vencimento no ativo mestre.
  """
  # 1. Salva o registro na tabela de histórico
  app_tables.historico_inspecoes.add_row(
    ativo=row_ativo,
    data_inspecao=dados_relatorio.get('data_inspecao'),
    tipo_inspecao=dados_relatorio.get('tipo_inspecao'),
    escopo=dados_relatorio.get('escopo'),
    parecer_conclusivo=dados_relatorio.get('parecer_conclusivo'),
    num_art=dados_relatorio.get('num_art'),
    pdf_relatorio=dados_relatorio.get('pdf_relatorio'),
    pdf_art=dados_relatorio.get('pdf_art')
  )

  # 2. Recalcula as datas de vencimento do ativo mestre
  recalcular_datas_ativo(row_ativo)


@anvil.server.callable
def buscar_inspecoes_por_ativo(ativo_pai):
  """
  Busca o histórico de inspeções da base de dados ordenado pela data mais recente.
  """
  inspecoes = app_tables.historico_inspecoes.search(
    tables.order_by("data_inspecao", ascending=False),
    ativo=ativo_pai
  )
  return list(inspecoes)

# --- GESTÃO INDEPENDENTE DE INSTRUMENTOS ---
@anvil.server.callable
def buscar_instrumentos_filtrados(tipo="Todos", exibir_historico=False):
  """Busca os instrumentos para a nova tela de gestão separada"""
  query = {}

  # Se NÃO marcou para exibir histórico, busca apenas os Ativos
  if not exibir_historico:
    query['status'] = "Ativo"

  if tipo and tipo != "Todos":
    query['tipo'] = tipo

  instrumentos = app_tables.dispositivos_seguranca.search(**query)
  hoje = datetime.date.today()
  lista = []

  for inst in instrumentos:
    st_calib = "Sem Data"
    if inst['prazo_calibracao']:
      st_calib = "Vencido" if inst['prazo_calibracao'] < hoje else "No Prazo"

    # Sobrepõe o status visual se a peça já foi trocada
    if inst['status'] == "Substituído" or inst['status'] == "Inativo":
      st_calib = "Arquivado"

    lista.append(dict(inst, status_calibracao=st_calib, row_objeto=inst))

  return lista

@anvil.server.callable
def executar_substituicao_instrumento(row_antigo, dados_novo, data_desativacao=None):
  """Desativa o antigo (Soft Delete) e cadastra o novo no mesmo equipamento"""
  # 1. Arquiva o antigo
  motivo = dados_novo.pop('motivo_troca', 'Substituição de rotina')
  if not data_desativacao:
    data_desativacao = datetime.date.today()
  row_antigo.update(
    status="Substituído",
    data_substituicao=data_desativacao,
    motivo_troca=motivo
  )

  # 2. Cria o novo vinculado ao mesmo ativo pai
  ativo_pai = row_antigo['ativo'] 
  novo_inst = app_tables.dispositivos_seguranca.add_row(
    ativo=ativo_pai,
    status="Ativo",
    **dados_novo
  )
  return novo_inst

@anvil.server.callable
def buscar_instrumentos_por_ativo(ativo_pai, exibir_historico=False):
  """
    Busca na base de dados todos os instrumentos que pertencem ao ativo selecionado.
    """
  if exibir_historico:
    instrumentos = app_tables.dispositivos_seguranca.search(ativo=ativo_pai)
  else:
    instrumentos = app_tables.dispositivos_seguranca.search(ativo=ativo_pai, status="Ativo")
  
  hoje = datetime.date.today()
  lista = []
  for inst in instrumentos:
    st_calib = "Sem Data"
    if inst['prazo_calibracao']:
      st_calib = "Vencido" if inst['prazo_calibracao'] < hoje else "No Prazo"
    if inst['status'] == "Substituído" or inst['status'] == "Inativo":
      st_calib = "Arquivado"
    
    lista.append(dict(inst, status_calibracao=st_calib, row_objeto=inst))
  return lista

@anvil.server.callable
def atualizar_data_substituicao(row_instrumento, nova_data):
  """Atualiza a data de desativação/substituição de um instrumento desativado"""
  if row_instrumento:
    row_instrumento.update(data_substituicao=nova_data)

# ---> ESTA É A FUNÇÃO NOVA QUE FALTAVA <---
@anvil.server.callable
def adicionar_novo_instrumento(ativo_pai, dados_instrumento):
  """
    Cadastra um instrumento de segurança totalmente novo 
    (sem ser substituição) e vincula ao ativo pai.
    """
  novo_inst = app_tables.dispositivos_seguranca.add_row(
    ativo=ativo_pai,
    status="Ativo",
    **dados_instrumento
  )
  return novo_inst


@anvil.server.callable
def remover_instrumento(instrumento_row):
    # Verifica se a linha foi passada corretamente e a deleta do banco
    if instrumento_row is not None:
      instrumento_row.delete()

@anvil.server.callable
def atualizar_inspecao(row_inspecao, dados_relatorio):
  """
  Atualiza uma inspeção existente no histórico e recalcula as datas no ativo mestre.
  """
  if not row_inspecao:
    return

  atualizacoes = {
    'data_inspecao': dados_relatorio.get('data_inspecao'),
    'tipo_inspecao': dados_relatorio.get('tipo_inspecao'),
    'escopo': dados_relatorio.get('escopo'),
    'parecer_conclusivo': dados_relatorio.get('parecer_conclusivo'),
    'num_art': dados_relatorio.get('num_art'),
  }

  # Atualiza os PDFs se novos arquivos foram carregados
  if dados_relatorio.get('pdf_relatorio') is not None:
    atualizacoes['pdf_relatorio'] = dados_relatorio.get('pdf_relatorio')
  if dados_relatorio.get('pdf_art') is not None:
    atualizacoes['pdf_art'] = dados_relatorio.get('pdf_art')

  row_inspecao.update(**atualizacoes)

  # Recalcula as datas de vencimento do ativo mestre
  recalcular_datas_ativo(row_inspecao['ativo'])

def recalcular_datas_ativo(row_ativo):
  """
  Busca a inspeção mais recente do ativo e atualiza as datas mestre (última e próxima inspeção).
  """
  if not row_ativo:
    return

  inspecoes = app_tables.historico_inspecoes.search(
    tables.order_by("data_inspecao", ascending=False),
    ativo=row_ativo
  )

  lista_inspecoes = list(inspecoes)
  if len(lista_inspecoes) > 0:
    mais_recente = lista_inspecoes[0]
    data_insp = mais_recente['data_inspecao']

    if data_insp:
      tipo = row_ativo['tipo']
      meses_validade = 12  # Prazo padrão de segurança (1 ano)

      # Regras de periodicidade conforme NR-13
      if tipo == "Caldeira":
        meses_validade = 12
      elif tipo == "Vaso de Pressão":
        meses_validade = 36
      elif tipo == "Tanque Metálico":
        meses_validade = 60
      elif "Tubulação" in tipo or "Sistemas" in tipo:
        meses_validade = 60

      # Soma os meses à data de inspeção
      ano_novo = data_insp.year + (data_insp.month + meses_validade - 1) // 12
      mes_novo = (data_insp.month + meses_validade - 1) % 12 + 1

      dias_no_mes = [31, 29 if ano_novo % 4 == 0 and not ano_novo % 100 == 0 or ano_novo % 400 == 0 else 28,
                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
      dia_novo = min(data_insp.day, dias_no_mes[mes_novo - 1])

      proxima_data = datetime.date(ano_novo, mes_novo, dia_novo)

      row_ativo.update(
        data_ultima_insp=data_insp,
        data_proxima_insp=proxima_data
      )
  else:
    # Se não houver mais nenhuma inspeção registrada para o ativo
    row_ativo.update(
      data_ultima_insp=None,
      data_proxima_insp=None
    )