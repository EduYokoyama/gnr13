from ._anvil_designer import LinhaAtivoTemplate
from anvil import *
import anvil.server

class LinhaAtivo(LinhaAtivoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      self.lbl_tag.text = self.item.get('tag', 'S/ TAG')
      self.lbl_tipo.text = self.item.get('tipo', 'S/ Tipo')

      st = self.item.get('status_inspeção', 'Sem Data')
      self.lbl_status.text = st

      cores = {
        "Vencido": "red", 
        "A Vencer (30 dias)": "orange", 
        "No Prazo": "green",
        "Sem Data": "gray"
      }
      self.lbl_status.foreground = cores.get(st, "gray")
      self.lbl_status.bold = True

  def btn_editar_click(self, **event_args):
    # Removida a tentativa de abrir o FormAtivoNR13 aqui para quebrar o Circular Import
    pass