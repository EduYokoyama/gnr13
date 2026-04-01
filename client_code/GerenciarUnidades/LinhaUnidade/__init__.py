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

      # Exibe a contagem vinda do servidor
      total = self.item.get('contagem_ativos', 0)
      self.lbl_total_ativos.text = f"📦 {total} ativos"

      # Estilização baseada na contagem
      if total > 0:
        self.lbl_total_ativos.foreground = "#2196F3" # Azul Anvil
        self.lbl_total_ativos.bold = True
      else:
        self.lbl_total_ativos.foreground = "gray"
        self.lbl_total_ativos.bold = False

  def btn_salvar_edit_click(self, **event_args):
    """Abre o diálogo de edição preenchido com os dados atuais"""
    from ..DialogUnidade import DialogUnidade
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

      # Atualiza visualmente a linha sem precisar recarregar tudo
      self.txt_nome_unidade.text = novos_dados['nome']
      self.lbl_localizacao.text = f"📍 {novos_dados['cidade']} - {novos_dados['estado']}"
      Notification("Unidade atualizada!", style="success").show()

  def btn_excluir_click(self, **event_args):
    """Remove a unidade após confirmação"""
    if confirm(f"Deseja excluir a unidade '{self.item.get('nome_unidade')}' permanentemente?"):
      anvil.server.call('excluir_unidade', self.item['row_objeto'])
      self.remove_from_parent()
      Notification("Unidade excluída.").show()