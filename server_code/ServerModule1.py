import anvil.server
from anvil.tables import app_tables
import anvil.media

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, dados_especificos, lista_instrumentos):
  """
    Função mestre que distribui os dados entre as tabelas Relacionais.
    """
  # 1. Cria o registro na Tabela Mestra 'ativos'
  novo_ativo_row = app_tables.ativos.add_row(
    tag=dados_mestre['tag'],
    nome_operacional=dados_mestre['nome_operacional'],
    tipo=dados_mestre['tipo'],
    unidade=dados_mestre['unidade'],
    fabricante=dados_mestre['fabricante'],
    ano_fabricacao=dados_mestre['ano_fabricacao'],
    data_proxima_insp=dados_mestre['data_proxima'],
    pdf_prontuario=dados_mestre['pdf_prontuario'],
    pdf_ultima_art=dados_mestre['pdf_art']
  )

  # 2. Identifica o tipo e salva na tabela de Specs correspondente
  # Adicionamos o link 'ativo' para relacionar com a linha criada acima
  dados_especificos['ativo'] = novo_ativo_row
  tipo = dados_mestre['tipo']

  if tipo == 'Vaso de Pressão':
    app_tables.specs_vasos.add_row(**dados_especificos)
  elif tipo == 'Caldeira':
    app_tables.specs_caldeiras.add_row(**dados_especificos)
  elif tipo == 'Tanque Metálico':
    app_tables.specs_tanques.add_row(**dados_especificos)
  elif tipo == 'Sistemas de Tubulação':
    app_tables.specs_tubulacoes.add_row(**dados_especificos)

    # 3. Salva os Instrumentos (Válvulas/Manômetros) vinculados
  for inst in lista_instrumentos:
    app_tables.dispositivos_seguranca.add_row(
      ativo=novo_ativo_row,
      status='Ativo',
      **inst
    )

  return True