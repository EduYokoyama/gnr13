from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.server

class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Lista expandida conforme requisitos técnicos de NR-13
    self.drp_tipo_inst.items = [
      "(Outro / Escrever...)",
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

  def drp_tipo_inst_change(self, **event_args):
    escolha = self.drp_tipo_inst.selected_value
    # Se escolher "Outro", liberamos o campo de texto para digitação manual
    if escolha == "(Outro / Escrever...)":
      self.txt_tipo_manual.visible = True
      self.txt_tipo_manual.text = "" 
    else:
      self.txt_tipo_manual.visible = False
      self.txt_tipo_manual.text = escolha 

  def txt_tipo_manual_change(self, **event_args):
    pass

  def btn_remover_click(self, **event_args):
    self.remove_from_parent()