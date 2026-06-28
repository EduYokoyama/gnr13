from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.server

# Limite de 30 MB em bytes
MAX_PDF_SIZE = 30 * 1024 * 1024

def _validar_pdf(arquivo, nome_campo):
  """Valida se o arquivo é PDF e se está dentro do limite de 30 MB."""
  if arquivo is None:
    return True
  nome = getattr(arquivo, 'name', '') or ''
  if not nome.lower().endswith('.pdf'):
    alert(f"O campo '{nome_campo}' aceita apenas arquivos PDF (.pdf).")
    return False
  tamanho = getattr(arquivo, 'length', 0) or 0
  if tamanho > MAX_PDF_SIZE:
    mb = tamanho / (1024 * 1024)
    alert(f"O arquivo '{nome}' tem {mb:.1f} MB. O limite máximo é de 30 MB.")
    return False
  return True


class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Lista expandida conforme requisitos técnicos de NR-13
    self.drp_tipo_inst.items = [
      "(Outro / Escrever...)",
      "Manômetro (Indicador de Pressão)",
      "Válvula de Segurança (PSV)",
      "Válvula de Alívio e Segurança (SRV)",
      "Válvula de Quebra Vácuo",
      "Disco de Ruptura",
      "Pressostato (Segurança/Controle)",
      "Termômetro / Pirômetro",
      "Transmissor de Pressão (PT)",
      "Transmissor de Temperatura (TT)",
      "Visor de Nível (Magnético/Vidro)",
      "Controlador de Nível (Eletrodo/Bóia)",
      "Fluxostato",
      "Sensor de Chama (Célula Fotoelétrica)",
      "Válvula Solenóide",
      "Válvula de Bloqueio Automático"
    ]

  def drp_tipo_inst_change(self, **event_args):
    escolha = self.drp_tipo_inst.selected_value
    # Se escolher "Outro", liberamos o campo de texto para digitação manual
    if escolha == "(Outro / Escrever...)":
      self.txt_tipo_manual.visible = True
      self.txt_tipo_manual.text = "" 
    else:
      self.txt_tipo_manual.visible = False
      self.txt_tipo_manual.text = escolha 

  def txt_tipo_manual_change(self, **event_args):
    pass

  # --- VALIDAÇÃO DE UPLOAD ---
  def file_cert_inst_change(self, **event_args):
    arquivo = self.file_cert_inst.file
    if not _validar_pdf(arquivo, "PDF Certificado"):
      self.file_cert_inst.clear()
      self.btn_ver_cert.visible = False
    else:
      self.btn_ver_cert.visible = arquivo is not None

  # --- VISUALIZAÇÃO DE PDF ---
  def btn_ver_cert_click(self, **event_args):
    arquivo = self.file_cert_inst.file
    if arquivo:
      try:
        url = arquivo.get_url(False)
        import anvil.js
        anvil.js.window.open(url, '_blank')
      except Exception as e:
        alert(f"Não foi possível abrir o PDF: {e}")
    else:
      alert("Selecione ou carregue um certificado PDF primeiro.")

  def btn_remover_click(self, **event_args):
    self.remove_from_parent()