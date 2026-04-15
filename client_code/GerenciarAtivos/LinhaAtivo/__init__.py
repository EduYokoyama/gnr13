from ._anvil_designer import LinhaAtivoTemplate
from GNR13.DialogInspecao import DialogInspecao # Importação absoluta
from anvil import *
import anvil.server

class LinhaAtivo(LinhaAtivoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      # Exibição de dados básicos
      self.lbl_tag.text = self.item.get('tag', 'S/ TAG')
      self.lbl_tipo.text = self.item.get('tipo', 'S/ Tipo')

      # Lógica de cores de status vinda do servidor [1]
      st = self.item.get('status_inspeção', 'Sem Data')
      self.lbl_status.text = st

      cores = {
        "Vencido": "#e74c3c",          # Vermelho
        "A Vencer (30 dias)": "#f39c12", # Laranja
        "No Prazo": "#2ecc71",         # Verde
        "Sem Data": "#95a5a6"          # Cinza
      }
      self.lbl_status.foreground = cores.get(st, "gray")
      self.lbl_status.bold = True

  @handle("btn_registrar_inspecao", "click")
  def btn_registrar_inspecao_click(self, **event_args):
    """Abre o diálogo para subir novo relatório de inspeção (Gatilho de Regularização)"""
    form_inspeção = DialogInspecao()

    # O alert gera os botões Virtuais (Salvar/Voltar)
    if alert(content=form_inspeção, title=f"Nova Inspeção: {self.item['tag']}", large=True, buttons=[("Salvar", True), ("Voltar", False)]):

      # Validação técnica: Relatório e ART são obrigatórios [7, 8]
      if not form_inspeção.file_relatorio.file or not form_inspeção.file_art.file:
        alert("Erro: Para conformidade NR-13, o Relatório e a ART são obrigatórios!")
        return

      dados_relatorio = {
        'data_inspecao': form_inspeção.dt_data_inspecao.date,
        'tipo_inspecao': form_inspeção.drp_tipo_inspecao.selected_value,
        'escopo': form_inspeção.drp_escopo.selected_value,
        'parecer_conclusivo': form_inspeção.chk_apto.checked,
        'num_art': form_inspeção.txt_num_art.text,
        'pdf_relatorio': form_inspeção.file_relatorio.file,
        'pdf_art': form_inspeção.file_art.file
      }

      # Envia ao servidor para calcular a nova data de vencimento
      anvil.server.call('processar_novo_relatorio', self.item['row_objeto'], dados_relatorio)
      Notification("Inspeção registrada! O status do ativo foi atualizado.", style="success").show()

      # Atualiza a lista pai para refletir a nova cor/status imediatamente
      self.parent.parent.parent.atualizar_lista()

  @handle("btn_editar", "click")
  def btn_editar_click(self, **event_args):
    """Abre o FormAtivoNR13 para edição. Importação local para evitar Circular Import."""
    from GNR13.FormAtivoNR13 import FormAtivoNR13

    # Passa o item atual para o formulário de cadastro em modo edição
    form_edicao = FormAtivoNR13(item_edicao=self.item)

    if alert(content=form_edicao, title=f"Editar Ativo: {self.item['tag']}", large=True, buttons=[]):
      self.parent.parent.parent.atualizar_lista()