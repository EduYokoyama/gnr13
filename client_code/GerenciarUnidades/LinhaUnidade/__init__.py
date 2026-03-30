from ._anvil_designer import LinhaUnidadeTemplate
from anvil import *
import anvil.server

class LinhaUnidade(LinhaUnidadeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      # Nome da Unidade
      self.txt_nome_unidade.text = self.item.get('nome_unidade', '')

      # Cidade - UF
      cidade = self.item.get('cidade') or "N/D"
      estado = self.item.get('estado') or "UF"
      self.lbl_localizacao.text = f"📍 {cidade} - {estado}"

      # Exibe a contagem
      total = self.item.get('contagem_ativos', 0)
      self.lbl_total_ativos.text = f"📦 {total} ativos"

      # CORREÇÃO DA LINHA 25: Usando .bold em vez de .font_weight
      if total > 0:
        self.lbl_total_ativos.foreground = "#2196F3" # Azul
        self.lbl_total_ativos.bold = True
      else:
        self.lbl_total_ativos.foreground = "gray"
        self.lbl_total_ativos.bold = False

  def btn_salvar_edit_click(self, **event_args):
    """Edição reusando o objeto original da linha"""
    from Controle_NR_13.DialogUnidade import DialogUnidade
    form_edicao = DialogUnidade()

    form_edicao.txt_nome.text = self.item.get('nome_unidade', '')
    form_edicao.txt_cep.text = self.item.get('cep', '')
    form_edicao.txt_cidade.text = self.item.get('cidade', '')
    form_edicao.drp_estado.selected_value = self.item.get('estado', None)
    form_edicao.txt_endereco.text = self.item.get('endereco_unidade', '')
    form_edicao.txt_telefone.text = self.item.get('telefone', '')
    form_edicao.txt_lat_long.text = self.item.get('lat_long', '')

    if alert(content=form_edicao, title="Editar Unidade", large=True, buttons=[("Salvar", True), ("Cancelar", False)]):
      novos_dados = {
        'nome': form_edicao.txt_nome.text,
        'cidade': form_edicao.txt_cidade.text,
        'estado': form_edicao.drp_estado.selected_value,
        'endereco': form_edicao.txt_endereco.text,
        'cep': form_edicao.txt_cep.text,
        'telefone': form_edicao.txt_telefone.text,
        'lat_long': form_edicao.txt_lat_long.text
      }
      anvil.server.call('editar_unidade', self.item['row_objeto'], novos_dados)
      self.txt_nome_unidade.text = novos_dados['nome']
      self.lbl_localizacao.text = f"📍 {novos_dados['cidade']} - {novos_dados['estado']}"
      Notification("Atualizado!").show()

  def btn_excluir_click(self, **event_args):
    if confirm("Excluir esta unidade permanentemente?"):
      anvil.server.call('excluir_unidade', self.item['row_objeto'])
      self.remove_from_parent()