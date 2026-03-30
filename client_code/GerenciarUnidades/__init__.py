from ._anvil_designer import GerenciarUnidadesTemplate
from anvil import *
import anvil.server

class GerenciarUnidades(GerenciarUnidadesTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.atualizar_lista()

  def atualizar_lista(self):
    # Procura o componente independente do nome (segurança extra)
    try:
      # Tenta pelo nome padrão que você deve usar
      self.repeating_panel_unidades.items = anvil.server.call('buscar_unidades')
    except AttributeError:
      # Se você esqueceu de renomear no design, ele avisa mas não trava o app todo
      alert("Atenção: Renomeie o Repeating Panel no Design para 'repeating_panel_unidades'")

  def btn_nova_unidade_click(self, **event_args):
    nome_novo = textbox_prompt("Digite o nome da nova Unidade Fabril:")
    if nome_novo:
      anvil.server.call('salvar_unidade', nome_novo)
      self.atualizar_lista()