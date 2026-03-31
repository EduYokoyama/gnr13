from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Preenchimento inicial dos DropDowns
    try:
      unidades_db = anvil.server.call('buscar_unidades')
      self.drp_unidade.items = [(u['nome_unidade'], u['row_objeto']) for u in unidades_db]
      self.drp_nome_fluido.items = anvil.server.call('buscar_fluidos_lista')

      # Opções fixas de Grupo conforme a Norma
      self.drp_grupo_fluido.items = ["Grupo A", "Grupo B", "Grupo C"]
    except:
      pass

    self.alternar_campos_equipamento()

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

  # --- LÓGICA DE FLUIDOS E CÁLCULO NR-13 ---

  def drp_nome_fluido_change(self, **event_args):
    nome = self.drp_nome_fluido.selected_value
    if nome:
      detalhes = anvil.server.call('obter_detalhes_fluido', nome)
      if detalhes:
        self.drp_grupo_fluido.selected_value = detalhes['grupo']
        self.lbl_comentario_fluido.text = detalhes['descricao']
        self.calcular_categoria()

  def calcular_categoria(self, **event_args):
    """Lógica oficial NR-13 para Vasos de Pressão"""
    try:
      p = float(self.num_pmta.text or 0) # Pressão em kgf/cm²
      v = float(self.num_volume.text or 0) # Volume em m³
      grupo = self.drp_grupo_fluido.selected_value

      # Na NR-13, a unidade de pressão para o cálculo de PV é MPa? 
      # Não, a norma usa P (MPa) x V (m³). 
      # Como você usa kgf/cm², 1 kgf/cm² ≈ 0.1 MPa.
      pv_norma = (p * 0.0980665) * v 
      pv_exibicao = p * v # O que você costuma ver em prontuários (kgf/cm² * m³)

      if pv_exibicao == 0 or not grupo:
        self.lbl_categoria_calculada.text = "Aguardando dados..."
        return

      cat = ""
      # Lógica baseada no Grupo de Potencial de Risco (Fluido) e PV (MPa*m³)
      # 100 kgf/cm²*m³ ≈ 10 MPa*m³ | 30 kgf/cm²*m³ ≈ 3 MPa*m³

      if "Grupo A" in grupo:
        if pv_exibicao >= 100: cat = "Categoria I"
        elif pv_exibicao >= 30: cat = "Categoria II"
        else: cat = "Categoria III"

      elif "Grupo B" in grupo:
        if pv_exibicao >= 100: cat = "Categoria I"
        elif pv_exibicao >= 30: cat = "Categoria II"
        else: cat = "Categoria III"

      elif "Grupo C" in grupo:
        if pv_exibicao >= 100: cat = "Categoria I"
        elif pv_exibicao >= 30: cat = "Categoria II"
        elif pv_exibicao >= 2.5: cat = "Categoria III"
        elif pv_exibicao >= 1: cat = "Categoria IV"
        else: cat = "Categoria V"

      self.lbl_categoria_calculada.text = f"P.V = {pv_exibicao:.2f} -> {cat}"
      self.lbl_categoria_calculada.foreground = "#2196F3"

    except:
      self.lbl_categoria_calculada.text = "Erro nos valores"

  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()
  def drp_grupo_fluido_change(self, **event_args): self.calcular_categoria()

  def btn_salvar_click(self, **event_args):
    # Lógica de salvar...
    pass

  @handle("btn_add_instrumento", "click")
  def btn_add_instrumento_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
