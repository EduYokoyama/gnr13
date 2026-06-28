from ._anvil_designer import GerenciarAtivosTemplate
from anvil import *
import anvil.server

class GerenciarAtivos(GerenciarAtivosTemplate):
  def __init__(self, filtro_status=None, filtro_apto=None, **properties):
    self.init_components(**properties)

    # Configuração inicial dos filtros
    try:
      # Busca unidades para o dropdown de filtro [3]
      unidades = anvil.server.call('buscar_unidades')
      self.drp_filtro_unidade.items = [("Todas Unidades", None)] + [(u['nome_unidade'], u['row_objeto']) for u in unidades]

      # Opções de Tipo e Status conforme a lógica do servidor [1, 4]
      self.drp_filtro_tipo.items = ["Todos", "Vaso de Pressão", "Caldeira", "Tanque Metálico", "Sistemas de Tubulação"]
      self.drp_filtro_status.items = ["Todos", "No Prazo", "A Vencer (30 dias)", "Vencido", "Sem Data"]
      self.drp_filtro_apto.items = [("Apto: Todos", "Todos"), ("Apto: Sim", "Sim"), ("Apto: Não", "Não")]

      if filtro_status:
        self.drp_filtro_status.selected_value = filtro_status
      if filtro_apto:
        self.drp_filtro_apto.selected_value = filtro_apto
    except Exception as e:
      print(f"Erro ao carregar filtros: {e}")

    # Carrega a lista pela primeira vez
    self.atualizar_lista()

  def atualizar_lista(self):
    """Chama o servidor para buscar dados filtrados e atualiza o RepeatingPanel"""
    u = self.drp_filtro_unidade.selected_value
    t = self.drp_filtro_tipo.selected_value
    s = self.drp_filtro_status.selected_value
    a = self.drp_filtro_apto.selected_value

    # O servidor retorna uma lista de dicionários com 'status_inspeção' calculado [1]
    self.repeating_panel_ativos.items = anvil.server.call('buscar_ativos_filtrados', u, t, s, a)

  def drp_filtros_change(self, **event_args):
    """Evento acionado por qualquer mudança nos 3 dropdowns de filtro"""
    self.atualizar_lista()