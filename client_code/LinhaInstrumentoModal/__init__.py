from ._anvil_designer import LinhaInstrumentoModalTemplate
from anvil import *
import anvil.server

class LinhaInstrumentoModal(LinhaInstrumentoModalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      # Preenche os campos com os dados da linha do banco
      self.lbl_tag.text = self.item.get('tag_instrumento', 'S/ TAG')
      self.lbl_tipo.text = self.item.get('tipo', '')

      # Lógica de Cores para o Status de Calibração
      st_calib = self.item.get('status_calibracao', 'Sem Data')
      self.lbl_status.text = st_calib
      self.lbl_status.bold = True

      if st_calib == "Arquivado":
        self.lbl_status.foreground = "gray"
        self.btn_substituir.visible = False # Peça arquivada não pode ser substituída de novo
      elif st_calib == "Vencido":
        self.lbl_status.foreground = "red"
      elif st_calib == "No Prazo":
        self.lbl_status.foreground = "green"

  def btn_substituir_click(self, **event_args):
    """Executa o 'Soft Delete': Arquiva o atual e prepara a entrada do novo"""
    txt_tag_novo = TextBox(placeholder="TAG do NOVO Instrumento")
    txt_motivo = TextBox(placeholder="Motivo (ex: Falha no teste)")

    painel = FlowPanel()
    painel.add_component(Label(text="TAG da nova peça:"))
    painel.add_component(txt_tag_novo)
    painel.add_component(Label(text="Motivo da troca:"))
    painel.add_component(txt_motivo)

    if alert(content=painel, title=f"Substituir {self.item['tag_instrumento']}", buttons=[("Confirmar", True), ("Cancelar", False)]):
      if not txt_tag_novo.text:
        alert("O TAG é obrigatório!")
        return

      dados_novo = {
        'tag_instrumento': txt_tag_novo.text,
        'tipo': self.item['tipo'], # Mantém o mesmo tipo do antigo
        'motivo_troca': txt_motivo.text
      }

      # Chama a função de servidor que desativa o antigo e cria o novo
      anvil.server.call('executar_substituicao_instrumento', self.item['row_objeto'], dados_novo)
      Notification("Substituição realizada! O histórico foi preservado.", style="success").show()

      # Atualiza a lista no formulário pai (o pop-up)
      self.parent.parent.parent.atualizar_lista()