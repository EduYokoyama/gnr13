from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server

class ItemTemplate2(ItemTemplate2Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    if self.item:
      self.lbl_tag.text = self.item.get('tag', 'S/ TAG')
      self.lbl_tipo.text = self.item.get('tipo', 'S/ Tipo')
      st = self.item.get('status_inspeção', 'Sem Data')
      self.lbl_status.text = st
      cores = {"Vencido": "red", "A Vencer (30 dias)": "orange", "No Prazo": "green"}
      self.lbl_status.foreground = cores.get(st, "gray")
      self.lbl_status.bold = True

  def btn_editar_click(self, **event_args):
    # ItemTemplate2 está dentro de ItemInstrumento, volta para a raiz para buscar o form
    try:
      from ..FormAtivoNR13 import FormAtivoNR13
    except ImportError:
      from .FormAtivoNR13 import FormAtivoNR13

    form_edicao = FormAtivoNR13(item_edicao=self.item)
    if alert(content=form_edicao, title=f"Editar Ativo: {self.item['tag']}", large=True, buttons=[]):
      try:
        self.parent.parent.parent.atualizar_lista()
      except:
        pass