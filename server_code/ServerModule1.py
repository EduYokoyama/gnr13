import anvil.server
from anvil.tables import app_tables

@anvil.server.callable
def salvar_ativo_completo(dados_mestre, dados_specs, lista_instrumentos):
  try:
    # 1. Salva na tabela ativos
    novo_ativo_row = app_tables.ativos.add_row(**dados_mestre)

    # 2. Salva Specs se for Vaso
    if dados_mestre['tipo'] == 'Vaso de Pressão':
      app_tables.specs_vasos.add_row(ativo=novo_ativo_row, **dados_specs)

    # 3. Salva Instrumentos vinculados (Tabela dispositivos_seguranca)
    for inst in lista_instrumentos:
      app_tables.dispositivos_seguranca.add_row(
        ativo=novo_ativo_row,
        tag_instrumento=inst['tag_instrumento'],
        num_serie=inst['num_serie'],
        data_calibracao=inst['data_calibracao'],
        prazo_calibracao=inst['prazo_calibracao'],
        certificado_pdf=inst['certificado_pdf'],
        status="Ativo"
      )
    return True
  except Exception as e:
    print(f"Erro no servidor: {e}")
    return False