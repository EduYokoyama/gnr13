from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files

class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def btn_remover_click(self, **event_args):
    """Remove esta linha visualmente do painel pai"""
    self.remove_from_parent()