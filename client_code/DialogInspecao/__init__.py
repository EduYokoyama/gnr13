from ._anvil_designer import DialogInspecaoTemplate
from anvil import *
import anvil.server
import datetime

# Limite de 30 MB em bytes
MAX_PDF_SIZE = 30 * 1024 * 1024

def _validar_pdf(arquivo, nome_campo):
  """Valida se o arquivo é PDF e se está dentro do limite de 30 MB.
  Retorna True se válido, False se inválido (e já mostra o alerta)."""
  if arquivo is None:
    return True  # nenhum arquivo selecionado é OK
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

def _abrir_pdf(media_obj):
  """Abre o PDF em uma nova aba do navegador."""
  try:
    url = media_obj.get_url(False)
    import anvil.js
    anvil.js.window.open(url, '_blank')
  except Exception as e:
    alert(f"Não foi possível abrir o PDF: {e}")


class DialogInspecao(DialogInspecaoTemplate):
  def __init__(self, inspecao_item=None, **properties):
    self.init_components(**properties)

    # Configuração dos itens conforme NR-13 e API 653
    self.drp_tipo_inspecao.items = ["Inicial", "Periódica", "Extraordinária"]
    self.drp_escopo.items = ["Exame Interno", "Exame Externo", "Ambos"]

    self.inspecao_item = inspecao_item

    if self.inspecao_item:
      self.dt_data_inspecao.date = self.inspecao_item['data_inspecao']
      self.drp_tipo_inspecao.selected_value = self.inspecao_item['tipo_inspecao']
      self.drp_escopo.selected_value = self.inspecao_item['escopo']
      self.chk_apto.checked = self.inspecao_item['parecer_conclusivo']
      self.txt_num_art.text = self.inspecao_item['num_art']

      # Mostra os botões de visualização se os arquivos já existem no banco
      if self.inspecao_item.get('arquivo_art'):
        self.btn_ver_art.visible = True
      if self.inspecao_item.get('arquivo_relatorio'):
        self.btn_ver_relatorio.visible = True
    else:
      # Data padrão = hoje (evita que o campo fique vazio e as datas não sejam salvas)
      self.dt_data_inspecao.date = datetime.date.today()
      # Valor padrão para segurança
      self.chk_apto.checked = False

  # --- VALIDAÇÃO DE UPLOAD ---
  def file_art_change(self, **event_args):
    arquivo = self.file_art.file
    if not _validar_pdf(arquivo, "PDF ART"):
      self.file_art.clear()
      self.btn_ver_art.visible = False
    else:
      # Mostra o botão de visualizar apenas se um novo arquivo foi carregado
      self.btn_ver_art.visible = arquivo is not None

  def file_relatorio_change(self, **event_args):
    arquivo = self.file_relatorio.file
    if not _validar_pdf(arquivo, "PDF Relatório"):
      self.file_relatorio.clear()
      self.btn_ver_relatorio.visible = False
    else:
      self.btn_ver_relatorio.visible = arquivo is not None

  # --- VISUALIZAÇÃO DE PDF ---
  def btn_ver_art_click(self, **event_args):
    # Tenta primeiro o arquivo recém-carregado no FileLoader; depois o salvo no banco
    arquivo = self.file_art.file
    if arquivo:
      _abrir_pdf(arquivo)
    elif self.inspecao_item and self.inspecao_item.get('arquivo_art'):
      _abrir_pdf(self.inspecao_item['arquivo_art'])
    else:
      alert("Nenhum arquivo ART disponível para visualização.")

  def btn_ver_relatorio_click(self, **event_args):
    arquivo = self.file_relatorio.file
    if arquivo:
      _abrir_pdf(arquivo)
    elif self.inspecao_item and self.inspecao_item.get('arquivo_relatorio'):
      _abrir_pdf(self.inspecao_item['arquivo_relatorio'])
    else:
      alert("Nenhum arquivo de Relatório disponível para visualização.")