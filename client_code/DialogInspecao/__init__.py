from ._anvil_designer import DialogInspecaoTemplate
from anvil import *
import anvil.server
import datetime

class DialogInspecao(DialogInspecaoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configuração dos itens conforme NR-13 e API 653
    self.drp_tipo_inspecao.items = ["Inicial", "Periódica", "Extraordinária"]
    self.drp_escopo.items = ["Exame Interno", "Exame Externo", "Ambos"]

    # Data padrão = hoje (evita que o campo fique vazio e as datas não sejam salvas)
    self.dt_data_inspecao.date = datetime.date.today()

    # Valor padrão para segurança
    self.chk_apto.checked = False