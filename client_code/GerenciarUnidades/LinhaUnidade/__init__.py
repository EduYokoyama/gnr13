from GNR13.DialogUnidade import DialogUnidade # Importação absoluta corrigida [4]
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
    form_edicao = DialogUnidade()
    # Preenche o form com os dados existentes para edição
    form_edicao.txt_nome.text = self.item.get('nome_unidade', '')
    form_edicao.txt_cidade.text = self.item.get('cidade', '')
    form_edicao.drp_estado.selected_value = self.item.get('estado', None)
    form_edicao.txt_endereco.text = self.item.get('endereco_unidade', '')
    form_edicao.txt_cep.text = self.item.get('cep', '')
    form_edicao.txt_telefone.text = self.item.get('telefone', '')
    form_edicao.txt_lat_long.text = self.item.get('lat_long', '')

    if alert(content=form_edicao, title="Editar Unidade", large=True, buttons=[("Salvar", True), ("Cancelar", False)]):
      # Mapeamento corrigido das colunas [1]
      novos_dados = {
        'nome_unidade': form_edicao.txt_nome.text, 
        'cidade': form_edicao.txt_cidade.text, 
        'estado': form_edicao.drp_estado.selected_value, 
        'endereco_unidade': form_edicao.txt_endereco.text, 
        'cep': form_edicao.txt_cep.text, 
        'telefone': form_edicao.txt_telefone.text, 
        'lat_long': form_edicao.txt_lat_long.text
      }

      # Chama o servidor passando o objeto da linha (row_objeto) criado no ServerModule [6, 7]
      anvil.server.call('editar_unidade', self.item['row_objeto'], novos_dados)

      # Atualiza a interface visual
      self.txt_nome_unidade.text = novos_dados['nome_unidade']
      self.lbl_localizacao.text = f"📍 {novos_dados['cidade']} - {novos_dados['estado']}"
      Notification("Unidade atualizada!", style="success").show()

  def btn_excluir_click(self, **event_args):
    if confirm(f"Deseja excluir permanentemente a unidade '{self.item['nome_unidade']}'?"):
      # O row_objeto é essencial para que o servidor saiba qual linha deletar [5, 7]
      anvil.server.call('excluir_unidade', self.item['row_objeto'])
      self.remove_from_parent()