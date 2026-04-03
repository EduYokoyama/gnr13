from ._anvil_designer import GerenciarAtivosTemplate
from anvil import *
import anvil.server

class GerenciarAtivos(GerenciarAtivosTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Preenche os DropDowns de filtro
    try:
      unidades = anvil.server.call('buscar_unidades')
      self.drp_filtro_unidade.items = [("Todas Unidades", None)] + [(u['nome_unidade'], u['row_objeto']) for u in unidades]
      self.drp_filtro_tipo.items = ["Todos", "Vaso de Pressão", "Sistema de Tubulação", "Caldeira"]
      self.drp_filtro_status.items = ["Todos", "No Prazo", "A Vencer (30 dias)", "Vencido", "Sem Data"]
    except:
      pass

    self.atualizar_lista()

  def atualizar_lista(self, **event_args):
    """Chama o servidor com os filtros do FlowPanel"""
    unidade = self.drp_filtro_unidade.selected_value
    tipo = self.drp_filtro_tipo.selected_value
    status = self.drp_filtro_status.selected_value

    # IMPORTANTE: Verifique se o nome no Design é 'repeating_panel_ativos'
    self.repeating_panel_ativos.items = anvil.server.call('buscar_ativos_filtrados', unidade, tipo, status)

  def drp_filtros_change(self, **event_args):
    self.atualizar_lista()