from ._anvil_designer import LinhaUnidadeTemplate
from anvil import *
import anvil.server

class LinhaUnidade(LinhaUnidadeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    if self.item:
      self.txt_nome_unidade.text = self.item.get('nome_unidade', '')
      self.lbl_localizacao.text = f"📍 {self.item.get('cidade', 'N/D')} - {self.item.get('estado', 'UF')}"
      total = self.item.get('contagem_ativos', 0)
      self.lbl_total_ativos.text = f"📦 {total} ativos"
      self.lbl_total_ativos.foreground = "#2196F3" if total > 0 else "gray"

  def btn_salvar_edit_click(self, **event_args):
    from ..DialogUnidade import DialogUnidade
    form_edicao = DialogUnidade()
    form_edicao.txt_nome.text = self.item.get('nome_unidade', '')
    form_edicao.drp_estado.selected_value = self.item.get('estado', None)

    if alert(content=form_edicao, title="Editar Unidade", large=True, buttons=[("Salvar", True), ("Cancelar", False)]):
      novos_dados = {'nome': form_edicao.txt_nome.text, 'cidade': form_edicao.txt_cidade.text, 'estado': form_edicao.drp_estado.selected_value, 'endereco': form_edicao.txt_endereco.text, 'cep': form_edicao.txt_cep.text, 'telefone': form_edicao.txt_telefone.text, 'lat_long': form_edicao.txt_lat_long.text}
      anvil.server.call('editar_unidade', self.item['row_objeto'], novos_dados)
      self.txt_nome_unidade.text = novos_dados['nome']
      Notification("Unidade atualizada!", style="success").show()

  def btn_excluir_click(self, **event_args):
    if confirm(f"Deseja excluir permanentemente?"):
      anvil.server.call('excluir_unidade', self.item['row_objeto'])
      self.remove_from_parent()