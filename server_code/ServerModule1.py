import anvil.server
from anvil.tables import app_tables
import anvil.media

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, dados_specs):
  """
    Função que organiza os dados nas tabelas e salva os arquivos no cofre.
    """
  try:
    # 1. Cria o registro na Tabela Mestra 'ativos'
    # Importante: 'unidade' deve ser a linha da tabela de unidades
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

    # 2. Salva os dados específicos na tabela correta
    tipo = dados_mestre['tipo']

    if tipo == 'Vaso de Pressão':
      app_tables.specs_vasos.add_row(
        ativo=novo_ativo_row, # Link para a tabela de ativos
        pmta=dados_specs['pmta'],
        volume=dados_specs['volume'],
        fluido_servico=dados_specs['fluido_servico'],
        categoria=dados_specs['categoria']
      )
    elif tipo == 'Caldeira':
      app_tables.specs_caldeiras.add_row(
        ativo=novo_ativo_row,
        cap_vapor=dados_specs['cap_vapor'],
        sup_aquecimento=dados_specs['sup_aquecimento'],
        combustivel=dados_specs['combustivel']
      )

    return True
  except Exception as e:
    print(f"Erro no servidor ao salvar: {e}")
    return False