from ._anvil_designer import LinhaInstrumentoTemplate
from anvil import *
import anvil.server

class LinhaInstrumento(LinhaInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # --- LIGAÇÃO DOS DADOS (DATA BINDING VIA CÓDIGO) ---
    if self.item:
      # Puxa o texto simples da base de dados
      self.lbl_tag.text = self.item['tag_instrumento']
      self.lbl_tipo.text = self.item['tipo']

      # Verifica e formata a data para o padrão DD/MM/AAAA
      prazo = self.item['prazo_calibracao']

      if prazo:
        self.lbl_vencimento.text = prazo.strftime('%d/%m/%Y')
      else:
        self.lbl_vencimento.text = "N/A"

  @handle("btn_excluir", "click")
  def btn_excluir_click(self, **event_args):
    """Pergunta se deseja excluir e remove a linha se confirmado"""
    tag = self.item['tag_instrumento']

    # Exibe um alerta de confirmação
    if confirm(f"Tem a certeza que deseja remover o instrumento {tag}?"):

      # 1. Manda o servidor apagar o registo da base de dados
      anvil.server.call('remover_instrumento', self.item)

      # 2. Mostra uma notificação verde de sucesso
      Notification(f"Instrumento {tag} removido.", style="success").show()

      # 3. Apaga esta linha visualmente do ecrã sem precisar recarregar tudo
      self.remove_from_parent()