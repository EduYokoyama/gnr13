from ._anvil_designer import LinhaInspecaoModalTemplate
from anvil import *
import anvil.server

class LinhaInspecaoModal(LinhaInspecaoModalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      # Formata a data se existir
      dt = self.item['data_inspecao']
      self.lbl_data.text = dt.strftime("%d/%m/%Y") if dt else "Sem Data"
      
      self.lbl_tipo.text = self.item['tipo_inspecao'] or ""
      self.lbl_escopo.text = self.item['escopo'] or ""
      
      # Parecer Conclusivo (Apto/Inapto)
      apto = self.item['parecer_conclusivo']
      if apto:
        self.lbl_parecer.text = "Apto"
        self.lbl_parecer.foreground = "green"
        self.lbl_parecer.bold = True
      else:
        self.lbl_parecer.text = "Inapto"
        self.lbl_parecer.foreground = "red"
        self.lbl_parecer.bold = True

  def btn_ver_relatorio_click(self, **event_args):
    """Baixa o PDF do relatório"""
    pdf = self.item['pdf_relatorio']
    if pdf:
      download(pdf)
    else:
      alert("Nenhum relatório anexado.")

  def btn_ver_art_click(self, **event_args):
    """Baixa o PDF da ART"""
    pdf = self.item['pdf_art']
    if pdf:
      download(pdf)
    else:
      alert("Nenhuma ART anexada.")

  def btn_editar_click(self, **event_args):
    """Abre o formulário de edição de inspeção"""
    from GNR13.DialogInspecao import DialogInspecao

    form_inspecao = DialogInspecao(inspecao_item=self.item)

    if alert(content=form_inspecao, title="Editar Inspeção", buttons=[("Salvar", True), ("Cancelar", False)], large=True):
      if not form_inspecao.dt_data_inspecao.date:
        alert("Erro: A data da inspeção é obrigatória!")
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

      # Atualiza a inspeção no servidor (irá recalcular as datas do ativo se necessário)
      anvil.server.call('atualizar_inspecao', self.item, dados_relatorio)
      Notification("Inspeção atualizada com sucesso!", style="success").show()

      # Recarrega a lista de inspeções na tela pai
      if hasattr(self.parent.parent.parent, 'atualizar_lista'):
        self.parent.parent.parent.atualizar_lista()