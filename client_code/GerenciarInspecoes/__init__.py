from ._anvil_designer import GerenciarInspecoesTemplate
from anvil import *
import anvil.server

class GerenciarInspecoes(GerenciarInspecoesTemplate):
  def __init__(self, ativo_pai=None, **properties):
    self.init_components(**properties)
    # Guarda a referência do Ativo que foi passado pelo Form principal
    self.ativo_pai = ativo_pai 

    # Atualiza a lista assim que a tela abre
    if self.ativo_pai:
      self.atualizar_lista()

  def atualizar_lista(self):
    """Busca no servidor o histórico de inspeções deste ativo"""
    if not self.ativo_pai: return
    self.rp_inspecoes.items = anvil.server.call('buscar_inspecoes_por_ativo', self.ativo_pai)

  def btn_novo_click(self, **event_args):
    """Abre o formulário para cadastrar uma nova inspeção"""
    from GNR13.DialogInspecao import DialogInspecao

    # Instancia o formulário de Inspeção
    form_inspecao = DialogInspecao()

    tag_nome = self.ativo_pai['tag'] if self.ativo_pai else ""

    # Abre o form como um alerta modal
    if alert(content=form_inspecao, title=f"Nova Inspeção: {tag_nome}", buttons=[("Salvar", True), ("Cancelar", False)], large=True):

      # Validação técnica: Relatório e ART são obrigatórios
      if not getattr(form_inspecao.file_relatorio, 'file', None) or not getattr(form_inspecao.file_art, 'file', None):
        alert("Erro: Para conformidade NR-13, o Relatório e a ART são obrigatórios!")
        return

      # Validação da data
      if not form_inspecao.dt_data_inspecao.date:
        alert("Erro: A data da inspeção é obrigatória para calcular o próximo vencimento!")
        return

      dados_relatorio = {
        'data_inspecao': form_inspecao.dt_data_inspecao.date,
        'tipo_inspecao': form_inspecao.drp_tipo_inspecao.selected_value,
        'escopo': form_inspecao.drp_escopo.selected_value,
        'parecer_conclusivo': form_inspecao.chk_apto.checked,
        'num_art': form_inspecao.txt_num_art.text,
        'pdf_relatorio': form_inspecao.file_relatorio.file,
        'pdf_art': form_inspecao.file_art.file
      }

      # Envia ao servidor para calcular a nova data de vencimento
      anvil.server.call('processar_novo_relatorio', self.ativo_pai, dados_relatorio)
      Notification("Inspeção registrada com sucesso!", style="success").show()

      # Atualiza a lista na tela
      self.atualizar_lista()