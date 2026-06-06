import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import datetime

@anvil.server.callable
def popular_banco_teste():
  """
  Limpa todo o banco e popula com dados de teste completos.
  - 2 ativos de cada tipo (8 total)
  - PSV + Manômetro para cada ativo
  - 1 ativo com inspeção vencida
  - 2 instrumentos com calibração vencida
  - 1 instrumento substituído
  """
  hoje = datetime.date.today()

  # =============================================
  # PASSO 1: LIMPAR TODAS AS TABELAS (ordem de dependências)
  # =============================================
  for r in app_tables.historico_inspecoes.search():
    r.delete()
  for r in app_tables.dispositivos_seguranca.search():
    r.delete()
  for r in app_tables.specs_vasos.search():
    r.delete()
  for r in app_tables.specs_caldeiras.search():
    r.delete()
  for r in app_tables.specs_tanques.search():
    r.delete()
  for r in app_tables.specs_tubulacoes.search():
    r.delete()
  for r in app_tables.ativos.search():
    r.delete()

  # =============================================
  # PASSO 2: GARANTIR QUE EXISTE UMA UNIDADE
  # =============================================
  unidade = app_tables.unidades.search()
  if len(unidade) == 0:
    unidade_ref = app_tables.unidades.add_row(
      nome_unidade="Planta Industrial Alpha",
      endereco_unidade="Rodovia BR-101, Km 45",
      cidade="Camaçari",
      estado="BA",
      cep="42810-000",
      telefone="(71) 3200-5000"
    )
  else:
    unidade_ref = list(unidade)[0]

  # =============================================
  # PASSO 3: CRIAR 2 VASOS DE PRESSÃO
  # =============================================
  
  # VP-001: Inspeção EM DIA (próxima em 2028)
  vp1 = app_tables.ativos.add_row(
    tag="VP-001",
    nome_operacional="Vaso Pulmão do Compressor C-01",
    tipo="Vaso de Pressão",
    unidade=unidade_ref,
    fabricante="Equipalcool Sistemas Industriais",
    status_prontuario="Original",
    ano_prontuario=2018,
    data_ultima_insp=datetime.date(2025, 3, 15),
    data_proxima_insp=datetime.date(2028, 3, 15)
  )
  app_tables.specs_vasos.add_row(
    ativo=vp1,
    pmta=12.5,
    volume=2.8,
    fluido_vaso="Ar",
    categoria="Categoria III (P.V: 35.00)",
    ano_fabricacao=2017,
    codigo_construcao="ASME SEC.VIII Div.1",
    ano_edicao_codigo=2015
  )
  app_tables.historico_inspecoes.add_row(
    ativo=vp1,
    data_inspecao=datetime.date(2025, 3, 15),
    tipo_inspecao="Periódica",
    escopo="Exame Interno",
    parecer_conclusivo=True,
    num_art="2025031500001"
  )

  # VP-002: Inspeção VENCIDA (este será o ativo com inspeção vencida)
  vp2 = app_tables.ativos.add_row(
    tag="VP-002",
    nome_operacional="Vaso Separador de Condensado V-12",
    tipo="Vaso de Pressão",
    unidade=unidade_ref,
    fabricante="CBC Indústrias Pesadas S.A.",
    status_prontuario="Reconstituído",
    ano_prontuario=2010,
    data_ultima_insp=datetime.date(2022, 6, 20),
    data_proxima_insp=datetime.date(2025, 1, 10)  # JÁ VENCEU
  )
  app_tables.specs_vasos.add_row(
    ativo=vp2,
    pmta=8.0,
    volume=5.2,
    fluido_vaso="Água",
    categoria="Categoria II (P.V: 41.60)",
    ano_fabricacao=2009,
    codigo_construcao="ASME SEC.VIII Div.1",
    ano_edicao_codigo=2007
  )
  app_tables.historico_inspecoes.add_row(
    ativo=vp2,
    data_inspecao=datetime.date(2022, 6, 20),
    tipo_inspecao="Periódica",
    escopo="Ambos",
    parecer_conclusivo=True,
    num_art="2022062000015"
  )

  # =============================================
  # PASSO 4: CRIAR 2 CALDEIRAS
  # =============================================
  
  cald1 = app_tables.ativos.add_row(
    tag="CLD-001",
    nome_operacional="Caldeira Flamotubular de Biomassa",
    tipo="Caldeira",
    unidade=unidade_ref,
    fabricante="ATA Combustão e Energia",
    status_prontuario="Original",
    ano_prontuario=2020,
    data_ultima_insp=datetime.date(2025, 1, 10),
    data_proxima_insp=datetime.date(2026, 1, 10)
  )
  app_tables.specs_caldeiras.add_row(
    ativo=cald1,
    cap_vapor=8000.0,
    sup_aquecimento=150.0,
    combustivel="Biomassa (Cavaco de Eucalipto)",
    ano_fabricacao=2019,
    codigo_construcao="ASME SEC.I",
    ano_edicao_codigo=2017
  )
  app_tables.historico_inspecoes.add_row(
    ativo=cald1,
    data_inspecao=datetime.date(2025, 1, 10),
    tipo_inspecao="Periódica",
    escopo="Exame Interno",
    parecer_conclusivo=True,
    num_art="2025011000003"
  )

  cald2 = app_tables.ativos.add_row(
    tag="CLD-002",
    nome_operacional="Caldeira Aquatubular a Gás Natural",
    tipo="Caldeira",
    unidade=unidade_ref,
    fabricante="Aalborg Industries do Brasil",
    status_prontuario="Original",
    ano_prontuario=2016,
    data_ultima_insp=datetime.date(2025, 5, 5),
    data_proxima_insp=datetime.date(2026, 5, 5)
  )
  app_tables.specs_caldeiras.add_row(
    ativo=cald2,
    cap_vapor=15000.0,
    sup_aquecimento=320.0,
    combustivel="Gás Natural (GN)",
    ano_fabricacao=2015,
    codigo_construcao="ASME SEC.I",
    ano_edicao_codigo=2013
  )
  app_tables.historico_inspecoes.add_row(
    ativo=cald2,
    data_inspecao=datetime.date(2025, 5, 5),
    tipo_inspecao="Periódica",
    escopo="Exame Externo",
    parecer_conclusivo=True,
    num_art="2025050500007"
  )

  # =============================================
  # PASSO 5: CRIAR 2 TANQUES METÁLICOS
  # =============================================
  
  tq1 = app_tables.ativos.add_row(
    tag="TQ-001",
    nome_operacional="Tanque de Armazenamento de Diesel S500",
    tipo="Tanque Metálico",
    unidade=unidade_ref,
    fabricante="Metalúrgica Orsitec",
    status_prontuario="Original",
    ano_prontuario=2014,
    data_ultima_insp=datetime.date(2024, 8, 12),
    data_proxima_insp=datetime.date(2029, 8, 12)
  )
  app_tables.specs_tanques.add_row(
    ativo=tq1,
    diametro_ext=6.1,
    volume_nominal=120.0,
    ano_fabricacao=2013,
    codigo_construcao="API 650",
    ano_edicao_codigo=2010
  )
  app_tables.historico_inspecoes.add_row(
    ativo=tq1,
    data_inspecao=datetime.date(2024, 8, 12),
    tipo_inspecao="Periódica",
    escopo="Exame Externo",
    parecer_conclusivo=True,
    num_art="2024081200022"
  )

  tq2 = app_tables.ativos.add_row(
    tag="TQ-002",
    nome_operacional="Tanque Pulmão de Água Desmineralizada",
    tipo="Tanque Metálico",
    unidade=unidade_ref,
    fabricante="Jaraguá Equipamentos Industriais",
    status_prontuario="Reconstituído",
    ano_prontuario=2008,
    data_ultima_insp=datetime.date(2023, 11, 3),
    data_proxima_insp=datetime.date(2028, 11, 3)
  )
  app_tables.specs_tanques.add_row(
    ativo=tq2,
    diametro_ext=3.5,
    volume_nominal=25.0,
    ano_fabricacao=2007,
    codigo_construcao="API 650",
    ano_edicao_codigo=2005
  )
  app_tables.historico_inspecoes.add_row(
    ativo=tq2,
    data_inspecao=datetime.date(2023, 11, 3),
    tipo_inspecao="Inicial",
    escopo="Ambos",
    parecer_conclusivo=True,
    num_art="2023110300018"
  )

  # =============================================
  # PASSO 6: CRIAR 2 SISTEMAS DE TUBULAÇÃO
  # =============================================
  
  tub1 = app_tables.ativos.add_row(
    tag="TUB-001",
    nome_operacional="Linha de Vapor Principal (Header 6\")",
    tipo="Sistemas de Tubulação",
    unidade=unidade_ref,
    fabricante="Montagem COMAU Industrial",
    status_prontuario="Original",
    ano_prontuario=2019,
    data_ultima_insp=datetime.date(2024, 4, 22),
    data_proxima_insp=datetime.date(2029, 4, 22)
  )
  app_tables.specs_tubulacoes.add_row(
    ativo=tub1,
    fluido_tub="Água",
    grupo_fluido="Grupo D",
    diametro_nominal="6\"",
    extensao=85.0,
    ano_fabricacao=2018,
    codigo_construcao="ASME B31.1",
    ano_edicao_codigo=2016,
    pmta=15.0,
    pressao_operacao=10.5,
    temp_projeto=250.0,
    espessura_minima=5.56,
    ativos_conectados=[cald1, vp1]
  )
  app_tables.historico_inspecoes.add_row(
    ativo=tub1,
    data_inspecao=datetime.date(2024, 4, 22),
    tipo_inspecao="Periódica",
    escopo="Exame Externo",
    parecer_conclusivo=True,
    num_art="2024042200010"
  )

  tub2 = app_tables.ativos.add_row(
    tag="TUB-002",
    nome_operacional="Linha de Ar Comprimido (Utilidades 4\")",
    tipo="Sistemas de Tubulação",
    unidade=unidade_ref,
    fabricante="Techint Engenharia",
    status_prontuario="Original",
    ano_prontuario=2021,
    data_ultima_insp=datetime.date(2025, 2, 18),
    data_proxima_insp=datetime.date(2030, 2, 18)
  )
  app_tables.specs_tubulacoes.add_row(
    ativo=tub2,
    fluido_tub="Ar",
    grupo_fluido="Grupo D",
    diametro_nominal="4\"",
    extensao=120.0,
    ano_fabricacao=2020,
    codigo_construcao="ASME B31.3",
    ano_edicao_codigo=2018,
    pmta=10.0,
    pressao_operacao=7.0,
    temp_projeto=60.0,
    espessura_minima=4.78,
    ativos_conectados=[vp1]
  )
  app_tables.historico_inspecoes.add_row(
    ativo=tub2,
    data_inspecao=datetime.date(2025, 2, 18),
    tipo_inspecao="Periódica",
    escopo="Exame Externo",
    parecer_conclusivo=True,
    num_art="2025021800005"
  )

  # =============================================
  # PASSO 7: INSTRUMENTOS DE SEGURANÇA
  # Para cada ativo: 1 PSV + 1 Manômetro
  # Requisitos especiais:
  #   - 2 instrumentos com calibração vencida
  #   - 1 instrumento substituído
  # =============================================
  
  todos_ativos = [vp1, vp2, cald1, cald2, tq1, tq2, tub1, tub2]
  tags_base = ["VP-001", "VP-002", "CLD-001", "CLD-002", "TQ-001", "TQ-002", "TUB-001", "TUB-002"]

  for i, (ativo, tag_base) in enumerate(zip(todos_ativos, tags_base)):
    
    # --- PSV (Válvula de Segurança) ---
    # Instrumento #0 do VP-002 (i=1): será a PSV SUBSTITUÍDA
    if i == 1:
      # PSV ANTIGA (substituída)
      psv_antiga = app_tables.dispositivos_seguranca.add_row(
        ativo=ativo,
        tag_instrumento=f"PSV-{tag_base}-OLD",
        tipo="Válvula de Segurança (PSV)",
        num_serie=f"PSV-SN-2018-{100+i}",
        data_calibracao=datetime.date(2022, 3, 10),
        prazo_calibracao=datetime.date(2023, 3, 10),
        ano_fabricacao=2018,
        status="Substituído",
        data_substituicao=datetime.date(2024, 7, 15),
        motivo_troca="Falha no teste de estanqueidade - vazamento pela sede"
      )
      # PSV NOVA (a que substituiu)
      app_tables.dispositivos_seguranca.add_row(
        ativo=ativo,
        tag_instrumento=f"PSV-{tag_base}",
        tipo="Válvula de Segurança (PSV)",
        num_serie=f"PSV-SN-2024-{200+i}",
        data_calibracao=datetime.date(2024, 7, 15),
        prazo_calibracao=datetime.date(2025, 7, 15),
        ano_fabricacao=2024,
        status="Ativo"
      )
    elif i == 3:
      # Instrumento do CLD-002 (i=3): PSV com calibração VENCIDA
      app_tables.dispositivos_seguranca.add_row(
        ativo=ativo,
        tag_instrumento=f"PSV-{tag_base}",
        tipo="Válvula de Segurança (PSV)",
        num_serie=f"PSV-SN-2020-{100+i}",
        data_calibracao=datetime.date(2023, 8, 20),
        prazo_calibracao=datetime.date(2024, 8, 20),  # VENCIDA
        ano_fabricacao=2020,
        status="Ativo"
      )
    else:
      # PSVs normais (em dia)
      app_tables.dispositivos_seguranca.add_row(
        ativo=ativo,
        tag_instrumento=f"PSV-{tag_base}",
        tipo="Válvula de Segurança (PSV)",
        num_serie=f"PSV-SN-2021-{100+i}",
        data_calibracao=datetime.date(2025, 1, 15),
        prazo_calibracao=datetime.date(2026, 1, 15),
        ano_fabricacao=2021,
        status="Ativo"
      )

    # --- Manômetro (Indicador de Pressão) ---
    if i == 5:
      # Instrumento do TQ-002 (i=5): Manômetro com calibração VENCIDA
      app_tables.dispositivos_seguranca.add_row(
        ativo=ativo,
        tag_instrumento=f"PI-{tag_base}",
        tipo="Manômetro (Indicador de Pressão)",
        num_serie=f"MAN-SN-2019-{300+i}",
        data_calibracao=datetime.date(2024, 2, 5),
        prazo_calibracao=datetime.date(2025, 2, 5),  # VENCIDA
        ano_fabricacao=2019,
        status="Ativo"
      )
    else:
      # Manômetros normais (em dia)
      app_tables.dispositivos_seguranca.add_row(
        ativo=ativo,
        tag_instrumento=f"PI-{tag_base}",
        tipo="Manômetro (Indicador de Pressão)",
        num_serie=f"MAN-SN-2022-{300+i}",
        data_calibracao=datetime.date(2025, 4, 1),
        prazo_calibracao=datetime.date(2026, 4, 1),
        ano_fabricacao=2022,
        status="Ativo"
      )

  return {
    'ativos_criados': 8,
    'instrumentos_criados': 17,  # 16 normais + 1 extra (PSV antiga substituída)
    'inspecoes_registradas': 8,
    'ativo_vencido': 'VP-002 (Vaso Separador de Condensado V-12)',
    'instrumentos_vencidos': [
      'PSV-CLD-002 (Calibração vencida em 2024-08-20)',
      'PI-TQ-002 (Calibração vencida em 2025-02-05)'
    ],
    'instrumento_substituido': 'PSV-VP-002-OLD → PSV-VP-002 (Substituído em 2024-07-15)'
  }
