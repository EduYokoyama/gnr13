from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server
from anvil.tables import app_tables

# Tentativa de importação flexível para matar o erro de módulo
try:
  from ..ItemInstrumento import ItemInstrumento
except:
  try:
    from .ItemInstrumento import ItemInstrumento
  except:
    from ItemInstrumento import ItemInstrumento

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # 1. Carrega Unidades
    try:
      self.drp_unidade.items = [(u['nome_unidade'], u) for u in app_tables.unidades.search() if u['nome_unidade']]
    except: pass

    # 2. Carrega Fluidos
    try:
      fluidos = app_tables.fluidos_referencia.search()
      self.drp_nome_fluido.items = [(f['nome_fluido'], f) for f in fluidos if f['nome_fluido']]
    except: pass

  @handle("btn_add_instrumento", "click")
  def btn_add_instrumento_click(self, **event_args):
    """Cria uma nova linha física e joga no painel_instrumentos"""
    nova_linha = ItemInstrumento()
    self.painel_instrumentos.add_component(nova_linha)

  def drp_tipo_equipamento_change(self, **event_args):
    self.card_vaso.visible = (self.drp_tipo_equipamento.selected_value == 'Vaso de Pressão')

  def drp_nome_fluido_change(self, **event_args):
    f = self.drp_nome_fluido.selected_value
    if f:
      self.drp_grupo_fluido.selected_value = f['grupo_nr13']
      self.lbl_comentario_fluido.text = f['comentario']
      self.calcular_categoria()

  def calcular_categoria(self, **event_args):
    try:
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      pv = p * v
      grupo = self.drp_grupo_fluido.selected_value
      if pv > 0 and grupo:
        cat = "I" if pv >= 100 else "II"
        self.lbl_categoria_calculada.text = f"CATEGORIA {cat} (P.V = {pv:.2f})"
    except: pass

  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()

  def btn_salvar_click(self, **event_args):
    if not self.txt_tag.text:
      alert("O TAG do Ativo é obrigatório.")
      return

    try:
      dados_mestre = {
        'tag': self.txt_tag.text,
        'nome_operacional': self.txt_nome_operacional.text,
        'tipo': self.drp_tipo_equipamento.selected_value,
        'unidade': self.drp_unidade.selected_value,
        'fabricante': self.txt_fabricante.text,
        'ano_fabricacao': int(self.num_ano.text or 0),
        'data_proxima_insp': self.dt_proxima_insp.date,
        'pdf_prontuario': self.file_prontuario.file,
        'pdf_ultima_art': self.file_ART.file
      }

      dados_specs = {}
      if dados_mestre['tipo'] == 'Vaso de Pressão':
        f_info = self.drp_nome_fluido.selected_value
        dados_specs = {
          'pmta': float(self.num_pmta.text or 0),
          'volume': float(self.num_volume.text or 0),
          'fluido_servico': f_info['nome_fluido'] if f_info else "N/A",
          'categoria': self.lbl_categoria_calculada.text
        }

      # COLETA FILTRADA: Varre o ColumnPanel ignorando o que estiver sem TAG
      instrumentos_finais = []
      for row in self.painel_instrumentos.get_components():
        if row.txt_tag_inst.text.strip():
          instrumentos_finais.append({
            'tag_instrumento': row.txt_tag_inst.text,
            'num_serie': row.txt_serie_inst.text,
            'data_calibracao': row.dt_calib_inst.date,
            'prazo_calibracao': row.dt_prazo_inst.date,
            'certificado_pdf': row.file_cert_inst.file
          })

      with Notification("Salvando Ativo e Instrumentos..."):
        if anvil.server.call('salvar_ativo_completo', dados_mestre, dados_specs, instrumentos_finais):
          alert("✅ Cadastro realizado com sucesso!")
          open_form('FormAtivoNR13')

    except Exception as e:
      alert(f"Erro ao salvar: {e}")