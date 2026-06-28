from ._anvil_designer import LinhaAtivoTemplate
from GNR13.GerenciarInspecoes import GerenciarInspecoes
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

      # Próxima Inspeção
      dt_prox = self.item.get('data_proxima_insp')
      self.lbl_proxima_insp.text = dt_prox.strftime("%d/%m/%Y") if dt_prox else "-"

      # Apto para Operar
      apto = self.item.get('apto_operar', 'Não')
      self.lbl_apto.text = apto
      self.lbl_apto.foreground = "#2ecc71" if apto == "Sim" else "#e74c3c"
      self.lbl_apto.bold = True

  @handle("btn_registrar_inspecao", "click")
  def btn_registrar_inspecao_click(self, **event_args):
    """Abre o gerenciador de inspeções mostrando o histórico do ativo"""
    form_inspecoes = GerenciarInspecoes(ativo_pai=self.item['row_objeto'])

    # O alert exibe a tela de gerenciamento de inspeções
    alert(content=form_inspecoes, title=f"Inspeções: {self.item['tag']}", large=True, buttons=[("Fechar", True)])

    # Ao fechar, atualiza a lista para refletir o novo status de inspeção
    self.parent.parent.parent.atualizar_lista()

  @handle("btn_editar", "click")
  def btn_editar_click(self, **event_args):
    """Abre o FormAtivoNR13 para edição. Importação local para evitar Circular Import."""
    from GNR13.FormAtivoNR13 import FormAtivoNR13

    # Passa o item atual para o formulário de cadastro em modo edição
    form_edicao = FormAtivoNR13(item_edicao=self.item)

    # 1. Abre a janela (o código 'pausa' aqui até a janela ser fechada)
    alert(content=form_edicao, title=f"Editar Ativo: {self.item['tag']}", large=True, buttons=[])

    # 2. Assim que fechar, atualiza a lista OBRIGATORIAMENTE
    self.parent.parent.parent.atualizar_lista()