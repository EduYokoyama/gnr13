from ._anvil_designer import LinhaUnidadeTemplate
from anvil import *
import anvil.server

class LinhaUnidade(LinhaUnidadeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    if self.item:
      self.txt_nome_unidade.text = self.item['nome_unidade']

  def btn_salvar_edit_click(self, **event_args):
    novo_nome = self.txt_nome_unidade.text
    if not novo_nome.strip():
      alert("O nome da unidade não pode estar vazio.")
      return
    anvil.server.call('atualizar_unidade', self.item, novo_nome)
    Notification("Unidade atualizada!").show()

  def btn_excluir_click(self, **event_args):
    if confirm(f"Excluir unidade '{self.item['nome_unidade']}'?"):
      anvil.server.call('excluir_unidade', self.item)
      self.remove_from_parent()