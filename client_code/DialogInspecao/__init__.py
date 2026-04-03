from ._anvil_designer import DialogInspecaoTemplate
from anvil import *
import anvil.server

class DialogInspecao(DialogInspecaoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configuração dos itens conforme NR-13 e API 653
    self.drp_tipo_inspecao.items = ["Inicial", "Periódica", "Extraordinária"]
    self.drp_escopo.items = ["Exame Interno", "Exame Externo", "Ambos"]

    # Valor padrão para segurança
    self.chk_apto.checked = False