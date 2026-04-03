from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # 1. Carregamento de DropDowns do Servidor
    try:
      unidades = anvil.server.call('buscar_unidades')
      self.drp_unidade.items = [(u['nome_unidade'], u['row_objeto']) for u in unidades]

      fluidos = anvil.server.call('buscar_fluidos_lista')
      self.drp_nome_fluido.items = fluidos      
      self.drp_fluido_tubo.items = fluidos      
      self.drp_grupo_fluido.items = ["Grupo A", "Grupo B", "Grupo C"]
    except Exception as e:
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
      "Sistemas de Tubulação": getattr(self, 'card_tubulacao', None),
      "Tubulação": getattr(self, 'card_tubulacao', None)
    }
    for c in cards.values():
      if c: c.visible = False
    if tipo in cards and cards[tipo]:
      cards[tipo].visible = True

  def _atualizar_dados_fluido(self, nome_fluido, contexto):
    if nome_fluido:
      detalhes = anvil.server.call('obter_detalhes_fluido', nome_fluido)
      if detalhes:
        if contexto == "vaso":
          self.drp_grupo_fluido.selected_value = detalhes['grupo']
          self.lbl_comentario_fluido.text = detalhes['descricao']
          self.calcular_categoria_vaso()
        else:
          self.lbl_grupo_tubo.text = detalhes['grupo']
          self.lbl_desc_fluido_tubo.text = detalhes['descricao']

  def drp_nome_fluido_change(self, **event_args):
    self._atualizar_dados_fluido(self.drp_nome_fluido.selected_value, "vaso")

  def drp_fluido_tubo_change(self, **event_args):
    self._atualizar_dados_fluido(self.drp_fluido_tubo.selected_value, "tubo")

  def calcular_categoria_vaso(self, **event_args):
    try:
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      grupo = self.drp_grupo_fluido.selected_value
      pv = p * v
      if pv == 0 or not grupo: return
      if "Grupo A" in grupo or "Grupo B" in grupo:
        cat = "Categoria I" if pv >= 100 else ("Categoria II" if pv >= 30 else "Categoria III")
      else:
        if pv >= 100: cat = "Categoria I"
        elif pv >= 30: cat = "Categoria II"
        elif pv >= 2.5: cat = "Categoria III"
        elif pv >= 1: cat = "Categoria IV"
        else: cat = "Categoria V"
      self.lbl_categoria_calculada.text = cat
    except: pass

  def btn_adicionar_instrumento_click(self, **event_args):
    from .ItemInstrumento import ItemInstrumento
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel: painel.add_component(ItemInstrumento())

  def btn_salvar_click(self, **event_args):
    from .ItemInstrumento import ItemInstrumento
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
      especificacoes = {
        'pmta': self.num_pmta.text, 'volume': self.num_volume.text, 
        'fluido_vaso': self.drp_nome_fluido.selected_value, 'categoria': self.lbl_categoria_calculada.text
      }
    elif any(x in tipo_eq for x in ["Tubulação", "Sistemas"]):
      especificacoes = {
        'fluido_tub': self.drp_fluido_tubo.selected_value, 'extensao': int(self.num_extensao.text or 0)
      }

    lista_instrumentos = []
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel:
      for row in painel.get_components():
        if isinstance(row, ItemInstrumento):
          try: ano = int(row.txt_ano_fab_inst.text) if row.txt_ano_fab_inst.text else None
          except: ano = None
          lista_instrumentos.append({
            'tag_instrumento': row.txt_tag_inst.text, 'tipo': row.txt_tipo_manual.text, 
            'num_serie': row.txt_serie_inst.text, 'ano_fabricacao': ano, 
            'data_calibracao': row.dt_calib_inst.date, 'prazo_calibracao': row.dt_prazo_inst.date, 'status': "Ativo"
          })

    if dados_mestre['tag'] and dados_mestre['unidade']:
      try:
        # Removido o item_edicao, envia None
        anvil.server.call('salvar_ativo_completo', dados_mestre, especificacoes, lista_instrumentos, None)
        Notification("Ativo salvo com sucesso!", style="success").show()
        self.limpar_tela()
      except Exception as e: alert(f"Erro ao salvar: {e}")
    else: alert("TAG e Unidade são obrigatórios!")

  def limpar_tela(self):
    self.txt_tag.text = ""
    self.txt_nome_operacional.text = ""
    self.txt_fabricante.text = ""
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel: painel.clear()

  def num_pmta_change(self, **event_args): self.calcular_categoria_vaso()
  def num_volume_change(self, **event_args): self.calcular_categoria_vaso()