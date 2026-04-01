from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server

try:
  from .ItemInstrumento import ItemInstrumento
except ImportError:
  try:
    from ..ItemInstrumento import ItemInstrumento
  except ImportError:
    ItemInstrumento = None

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    try:
      self.drp_unidade.items = [(u['nome_unidade'], u['row_objeto']) for u in anvil.server.call('buscar_unidades')]
      self.drp_nome_fluido.items = anvil.server.call('buscar_fluidos_lista')
      self.drp_grupo_fluido.items = ["Grupo A", "Grupo B", "Grupo C"]
    except Exception as e:
      print(f"Erro no carregamento: {e}")

    self.alternar_campos_equipamento()

  def btn_adicionar_instrumento_click(self, **event_args):
    """Adiciona linha de instrumento ao painel fp_instrumentos"""
    if ItemInstrumento:
      painel = getattr(self, 'fp_instrumentos', None) or getattr(self, 'card_instrumentos', None)
      if painel:
        painel.add_component(ItemInstrumento())
    else:
      alert("Erro: ItemInstrumento não encontrado.")

  def drp_tipo_equipamento_change(self, **event_args):
    self.alternar_campos_equipamento()

  def alternar_campos_equipamento(self):
    tipo = self.drp_tipo_equipamento.selected_value
    cards = {
      "Vaso de Pressão": getattr(self, 'card_vaso', None),
      "Caldeira": getattr(self, 'card_caldeira', None),
      "Tanque Metálico": getattr(self, 'card_tanque', None),
      "Tubulação": getattr(self, 'card_tubulacao', None)
    }
    for c in cards.values():
      if c: c.visible = False
    if tipo in cards and cards[tipo]:
      cards[tipo].visible = True

  def drp_nome_fluido_change(self, **event_args):
    nome = self.drp_nome_fluido.selected_value
    if nome:
      detalhes = anvil.server.call('obter_detalhes_fluido', nome)
      if detalhes:
        self.drp_grupo_fluido.selected_value = detalhes['grupo']
        self.lbl_comentario_fluido.text = detalhes['descricao']
        self.calcular_categoria()

  def calcular_categoria(self, **event_args):
    try:
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      grupo = self.drp_grupo_fluido.selected_value
      pv = p * v
      if pv == 0 or not grupo:
        self.lbl_categoria_calculada.text = "Aguardando dados..."
        return
      if "Grupo A" in grupo or "Grupo B" in grupo:
        cat = "Categoria I" if pv >= 100 else ("Categoria II" if pv >= 30 else "Categoria III")
      else:
        if pv >= 100: cat = "Categoria I"
        elif pv >= 30: cat = "Categoria II"
        elif pv >= 2.5: cat = "Categoria III"
        elif pv >= 1: cat = "Categoria IV"
        else: cat = "Categoria V"
      self.lbl_categoria_calculada.text = f"P.V = {pv:.2f} -> {cat}"
      self.lbl_categoria_calculada.foreground = "#2196F3"
    except:
      self.lbl_categoria_calculada.text = "Erro"

  def btn_salvar_click(self, **event_args):
    tipo_eq = self.drp_tipo_equipamento.selected_value
    dados_mestre = {
      'tag': self.txt_tag.text,
      'nome_operacional': self.txt_nome_operacional.text,
      'unidade': self.drp_unidade.selected_value,
      'tipo': tipo_eq,
      'fabricante': self.txt_fabricante.text
    }
    especificacoes = {}
    if tipo_eq == "Vaso de Pressão":
      especificacoes = {'pmta': self.num_pmta.text, 'volume': self.num_volume.text, 'fluido': self.drp_nome_fluido.selected_value, 'categoria': self.lbl_categoria_calculada.text}

    # Coleta de dispositivos da tabela dispositivos_seguranca
    lista_instrumentos = []
    painel = getattr(self, 'fp_instrumentos', None) or getattr(self, 'card_instrumentos', None)
    if painel:
      for row in painel.get_components():
        if isinstance(row, ItemInstrumento):
          lista_instrumentos.append({
            'tag': row.txt_tag_inst.text,
            'tipo': row.txt_tipo_manual.text, # Campo unificado (Dropdown ou Manual)
            'serie': row.txt_serie_inst.text, 
            'ano_fab': row.txt_ano_fab_inst.text,
            'data_cal': row.dt_calib_inst.date,
            'prazo': row.dt_prazo_inst.date, # Date conforme sua tabela
            'status': "Ativo"
          })

    if dados_mestre['tag'] and dados_mestre['unidade']:
      anvil.server.call('salvar_ativo_completo', dados_mestre, especificacoes, lista_instrumentos)
      Notification("Salvo com sucesso!", style="success").show()
      self.limpar_tela()
    else:
      alert("Preencha TAG e Unidade.")

  def limpar_tela(self):
    self.txt_tag.text = ""
    painel = getattr(self, 'fp_instrumentos', None) or getattr(self, 'card_instrumentos', None)
    if painel: painel.clear()

  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()
  def drp_grupo_fluido_change(self, **event_args): self.calcular_categoria()