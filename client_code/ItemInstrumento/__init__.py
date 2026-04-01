from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.server

class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.lista_sugestoes = [
      "Válvula de Segurança (PSV)", "Manômetro", "Pressostato", "Termostato", 
      "Disco de Ruptura", "Transmissor de Pressão", "Transdutor de Pressão", 
      "Termopar / PT-100", "Manovacuômetro", "Válvula de Alívio", 
      "Sensor de Nível / Garrafa", "Fluxostato", "Vacuômetro"
    ]
    self.drp_tipo_inst.items = ["(Outro / Escrever...)"] + sorted(self.lista_sugestoes)

  def drp_tipo_inst_change(self, **event_args):
    escolha = self.drp_tipo_inst.selected_value
    if escolha == "(Outro / Escrever...)":
      self.txt_tipo_manual.visible = True
      self.txt_tipo_manual.text = "" 
      self.txt_tipo_manual.focus()
    else:
      self.txt_tipo_manual.visible = False
      self.txt_tipo_manual.text = escolha 

  def txt_tipo_manual_change(self, **event_args):
    if self.txt_tipo_manual.text != "":
      if self.drp_tipo_inst.selected_value != "(Outro / Escrever...)":
        self.drp_tipo_inst.selected_value = "(Outro / Escrever...)"

  def btn_remover_click(self, **event_args):
    self.remove_from_parent()