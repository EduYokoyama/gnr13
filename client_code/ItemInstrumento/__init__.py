from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.server

class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  @handle("btn_remover", "click")
  def btn_remover_click(self, **event_args):
    """Remove esta linha visualmente"""
    self.remove_from_parent()