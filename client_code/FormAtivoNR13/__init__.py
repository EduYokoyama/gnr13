from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server
from anvil.tables import app_tables

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    try:
      self.drp_unidade.items = [(u['nome_unidade'], u) for u in app_tables.unidades.search() if u['nome_unidade']]
      self.drp_nome_fluido.items = [(f['nome_fluido'], f) for f in app_tables.fluidos_referencia.search() if f['nome_fluido']]
    except: pass

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
        self.lbl_categoria_calculada.foreground = "blue"
    except: pass

  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()

  def btn_add_instrumento_click(self, **event_args):
    # Importação absoluta para evitar ModuleNotFoundError
    from Controle_NR_13.ItemInstrumento import ItemInstrumento
    self.card_instrumentos.add_component(ItemInstrumento())

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
      instrumentos = []
      for row in self.card_instrumentos.get_components():
        if hasattr(row, 'txt_tag_inst') and row.txt_tag_inst.text.strip():
          instrumentos.append({
            'tag_instrumento': row.txt_tag_inst.text,
            'num_serie': row.txt_serie_inst.text,
            'data_calibracao': row.dt_calib_inst.date,
            'prazo_calibracao': row.dt_prazo_inst.date,
            'certificado_pdf': row.file_cert_inst.file
          })

      with Notification("Salvando Ativo..."):
        if anvil.server.call('salvar_ativo_completo', dados_mestre, {}, instrumentos):
          alert("✅ Cadastro realizado com sucesso!")
          self.txt_tag.text = ""
          self.card_instrumentos.clear()
    except Exception as e:
      alert(f"Erro ao salvar: {e}")