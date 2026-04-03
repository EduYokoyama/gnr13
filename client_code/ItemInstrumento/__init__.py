from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.server

class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.drp_tipo_inst.items = ["(Outro / Escrever...)", "Manômetro", "Pressostato", "Válvula de Segurança (PSV)"]

  def drp_tipo_inst_change(self, **event_args):
    escolha = self.drp_tipo_inst.selected_value
    if escolha == "(Outro / Escrever...)":
      self.txt_tipo_manual.visible = True
      self.txt_tipo_manual.text = "" 
    else:
      self.txt_tipo_manual.visible = False
      self.txt_tipo_manual.text = escolha 

  def btn_remover_click(self, **event_args):
    self.remove_from_parent()