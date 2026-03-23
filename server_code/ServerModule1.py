import anvil.server
from anvil.tables import app_tables
import anvil.media

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, dados_specs, lista_instrumentos): # <--- ADICIONADO o 3º parâmetro
  """
  Função que organiza os dados nas tabelas e salva os arquivos no cofre.
  """
  try:
    # 1. Cria o registro na Tabela Mestra 'ativos'
    novo_ativo_row = app_tables.ativos.add_row(
      tag=dados_mestre['tag'],
      nome_operacional=dados_mestre['nome_operacional'],
      tipo=dados_mestre['tipo'],
      unidade=dados_mestre['unidade'],
      fabricante=dados_mestre['fabricante'],
      ano_fabricacao=dados_mestre['ano_fabricacao'],
      data_proxima_insp=dados_mestre['data_proxima_insp'], # <-- CORRIGIDO AQUI
      pdf_prontuario=dados_mestre['pdf_prontuario'],
      pdf_ultima_art=dados_mestre['pdf_ultima_art'] # <-- CORRIGIDO AQUI PARA BATER COM O FORMULÁRIO
    )

    # 2. Salva os dados específicos na tabela correta
    tipo = dados_mestre['tipo']

    if tipo == 'Vaso de Pressão':
      app_tables.specs_vasos.add_row(
        ativo=novo_ativo_row,
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

    # 3. NOVO: Salva os instrumentos (Válvulas) vinculados a este Ativo
    for inst in lista_instrumentos:
      app_tables.dispositivos_seguranca.add_row(
        ativo=novo_ativo_row,
        tag_instrumento=inst.get('tag_instrumento', 'S/N'),
        status='Ativo'
      )

    return True
  except Exception as e:
    # Isso aqui vai imprimir o erro real no console do Anvil se algo falhar
    print(f"Erro no servidor ao salvar: {e}")
    return False
