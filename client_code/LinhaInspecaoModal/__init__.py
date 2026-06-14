from ._anvil_designer import LinhaInspecaoModalTemplate
from anvil import *
import anvil.server

class LinhaInspecaoModal(LinhaInspecaoModalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      # Formata a data se existir
      dt = self.item.get('data_inspecao')
      self.lbl_data.text = dt.strftime("%d/%m/%Y") if dt else "Sem Data"
      
      self.lbl_tipo.text = self.item.get('tipo_inspecao', '')
      self.lbl_escopo.text = self.item.get('escopo', '')
      
      # Parecer Conclusivo (Apto/Inapto)
      apto = self.item.get('parecer_conclusivo')
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
    pdf = self.item.get('pdf_relatorio')
    if pdf:
      download(pdf)
    else:
      alert("Nenhum relatório anexado.")

  def btn_ver_art_click(self, **event_args):
    """Baixa o PDF da ART"""
    pdf = self.item.get('pdf_art')
    if pdf:
      download(pdf)
    else:
      alert("Nenhuma ART anexada.")