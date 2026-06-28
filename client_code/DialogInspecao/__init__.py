from ._anvil_designer import DialogInspecaoTemplate
from anvil import *
import anvil.server
import datetime

class DialogInspecao(DialogInspecaoTemplate):
  def __init__(self, inspecao_item=None, **properties):
    self.init_components(**properties)

    # Configuração dos itens conforme NR-13 e API 653
    self.drp_tipo_inspecao.items = ["Inicial", "Periódica", "Extraordinária"]
    self.drp_escopo.items = ["Exame Interno", "Exame Externo", "Ambos"]

    self.inspecao_item = inspecao_item

    if self.inspecao_item:
      self.dt_data_inspecao.date = self.inspecao_item['data_inspecao']
      self.drp_tipo_inspecao.selected_value = self.inspecao_item['tipo_inspecao']
      self.drp_escopo.selected_value = self.inspecao_item['escopo']
      self.chk_apto.checked = self.inspecao_item['parecer_conclusivo']
      self.txt_num_art.text = self.inspecao_item['num_art']
    else:
      # Data padrão = hoje (evita que o campo fique vazio e as datas não sejam salvas)
      self.dt_data_inspecao.date = datetime.date.today()
      # Valor padrão para segurança
      self.chk_apto.checked = False