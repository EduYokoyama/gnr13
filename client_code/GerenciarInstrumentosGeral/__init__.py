from ._anvil_designer import GerenciarInstrumentosGeralTemplate
from anvil import *
import anvil.server

class GerenciarInstrumentosGeral(GerenciarInstrumentosGeralTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configuração inicial dos filtros
    try:
      # Busca as unidades para o dropdown de filtro
      unidades = anvil.server.call('buscar_unidades')
      self.drp_filtro_unidade.items = [("Todas as Unidades", None)] + [(u['nome_unidade'], u['row_objeto']) for u in unidades]

      # Filtros de Tipo de Ativo
      self.drp_filtro_tipo_ativo.items = [("Todos Tipos de Ativo", "Todos"), "Vaso de Pressão", "Caldeira", "Tanque Metálico", "Sistemas de Tubulação"]

      # Filtros de Tipo de Instrumento
      self.drp_filtro_tipo_inst.items = [
        ("Todos Tipos de Instrumento", "Todos"),
        "Manômetro (Indicador de Pressão)",
        "Válvula de Segurança (PSV)",
        "Válvula de Alívio e Segurança (SRV)",
        "Válvula de Quebra Vácuo",
        "Disco de Ruptura",
        "Pressostato (Segurança/Controle)",
        "Termômetro / Pirômetro",
        "Transmissor de Pressão (PT)",
        "Transmissor de Temperatura (TT)",
        "Visor de Nível (Magnético/Vidro)",
        "Controlador de Nível (Eletrodo/Bóia)",
        "Fluxostato",
        "Sensor de Chama (Célula Fotoelétrica)",
        "Válvula Solenóide",
        "Válvula de Bloqueio Automático"
      ]

      # Filtros de Status do Instrumento
      self.drp_filtro_status.items = [
        ("Todos os Status", "Todos"),
        ("Ativo", "Ativo"),
        ("Inativo", "Inativo"),
        ("Substituído", "Substituído")
      ]
    except Exception as e:
      print(f"Erro ao carregar filtros: {e}")

    # Carrega a lista pela primeira vez
    self.atualizar_lista()

  def atualizar_lista(self):
    """Busca do servidor todos os instrumentos filtrados e atualiza a listagem"""
    u = self.drp_filtro_unidade.selected_value
    ta = self.drp_filtro_tipo_ativo.selected_value
    ti = self.drp_filtro_tipo_inst.selected_value
    st = self.drp_filtro_status.selected_value

    self.repeating_panel_instrumentos.items = anvil.server.call('buscar_instrumentos_filtrados', u, ta, ti, st)

  def drp_filtros_change(self, **event_args):
    self.atualizar_lista()
