from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, item_edicao=None, **properties):
    self.init_components(**properties)
    self.item_edicao = item_edicao

    # 1. Carregamento de Dropdowns e Dados Iniciais
    try:
      unidades = anvil.server.call('buscar_unidades')
      self.drp_unidade.items = [(u['nome_unidade'], u['row_objeto']) for u in unidades]

      fluidos = anvil.server.call('buscar_fluidos_lista')
      self.drp_nome_fluido.items = fluidos
      self.drp_fluido_tubo.items = fluidos

      self.drp_status_prontuario.items = ["Original", "Reconstituído"]
      self.drp_tipo_equipamento.items = ["Vaso de Pressão", "Caldeira", "Tanque Metálico", "Sistemas de Tubulação"]
    except Exception as e:
      print(f"Erro no carregamento inicial: {e}")

    # 2. Direcionamento de Fluxo (Edição vs Novo)
    if self.item_edicao:
      self.preencher_dados_edicao()
    else:
      self.alternar_campos_equipamento()

  def preencher_dados_edicao(self):
    it = self.item_edicao
    self.txt_tag.text = it.get('tag')
    self.txt_nome_operacional.text = it.get('nome_operacional')
    self.txt_fabricante.text = it.get('fabricante')
    self.drp_unidade.selected_value = it.get('unidade')
    self.drp_tipo_equipamento.selected_value = it.get('tipo')
    self.drp_status_prontuario.selected_value = it.get('status_prontuario', "Original")
    self.num_ano_prontuario.text = it.get('ano_prontuario')

    specs = anvil.server.call('obter_specs_ativo', it['row_objeto'])
    if specs:
      tipo = it['tipo']
      if tipo == "Vaso de Pressão":
        self.num_ano_vaso.text = specs.get('ano_fabricacao')
        self.txt_cod_vaso.text = specs.get('codigo_construcao')
        self.num_pmta.text = specs.get('pmta')
        self.num_volume.text = specs.get('volume')
        self.drp_nome_fluido.selected_value = specs.get('fluido_vaso')
      elif tipo == "Caldeira":
        self.num_ano_caldeira.text = specs.get('ano_fabricacao')
        self.txt_cod_caldeira.text = specs.get('codigo_construcao')
      elif "Tubulação" in tipo:
        self.drp_fluido_tubo.selected_value = specs.get('fluido_tub')
        self.num_extensao.text = specs.get('extensao')
    self.alternar_campos_equipamento()

  def drp_tipo_equipamento_change(self, **event_args):
    self.alternar_campos_equipamento()

  def alternar_campos_equipamento(self):
    """Exibe o card técnico correto de acordo com a norma aplicável."""
    tipo = self.drp_tipo_equipamento.selected_value
    cards = {
      "Vaso de Pressão": self.card_vaso,
      "Caldeira": self.card_caldeira,
      "Tanque Metálico": self.card_tanque,
      "Sistemas de Tubulação": self.card_tubulacao
    }
    for c in cards.values(): 
      if c: c.visible = False
    if tipo in cards and cards[tipo]: 
      cards[tipo].visible = True

  # --- EVENTOS DE FLUIDO E CATEGORIZAÇÃO ---

  def drp_nome_fluido_change(self, **event_args):
    """Atualiza dados do fluido para Vasos de Pressão."""
    nome = self.drp_nome_fluido.selected_value
    if nome:
      det = anvil.server.call('obter_detalhes_fluido', nome)
      self.drp_grupo_fluido.selected_value = det['grupo']
      self.lbl_comentario_fluido.text = det['descricao']
      self.calcular_categoria()

  def drp_fluido_tubo_change(self, **event_args):
    """CORREÇÃO: Atualiza dados do fluido para Sistemas de Tubulação."""
    nome = self.drp_fluido_tubo.selected_value
    if nome:
      det = anvil.server.call('obter_detalhes_fluido', nome)
      if hasattr(self, 'lbl_grupo_tubo'):
        self.lbl_grupo_tubo.text = det['grupo']
        self.lbl_desc_fluido_tubo.text = det['descricao']

  def calcular_categoria(self, **event_args):
    """Cérebro NR-13: Categorização baseada em P.V e Classe de Fluido."""
    try:
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      pv = p * v
      grupo = self.drp_grupo_fluido.selected_value
      if pv <= 0 or not grupo: return

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

  # --- GESTÃO DE INSTRUMENTOS ---

  def btn_adicionar_instrumento_click(self, **event_args):
    """CORREÇÃO: Adiciona um novo ItemInstrumento ao painel dinâmico."""
    from GNR13.ItemInstrumento import ItemInstrumento
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel:
      painel.add_component(ItemInstrumento())

  # --- SALVAMENTO E LIMPEZA ---

  def btn_salvar_click(self, **event_args):
    from GNR13.ItemInstrumento import ItemInstrumento
    tipo_eq = self.drp_tipo_equipamento.selected_value

    dados_mestre = {
      'tag': self.txt_tag.text,
      'nome_operacional': self.txt_nome_operacional.text,
      'unidade': self.drp_unidade.selected_value,
      'tipo': tipo_eq,
      'fabricante': self.txt_fabricante.text,
      'pdf_prontuario': self.file_prontuario.file,
      'status_prontuario': self.drp_status_prontuario.selected_value,
      'ano_prontuario': self.num_ano_prontuario.text
    }

    especificacoes = {}
    if tipo_eq == "Vaso de Pressão":
      especificacoes = {
        'ano_fabricacao': self.num_ano_vaso.text,
        'codigo_construcao': self.txt_cod_vaso.text,
        'ano_edicao_codigo': self.num_edicao_vaso.text,
        'pmta': self.num_pmta.text,
        'volume': self.num_volume.text,
        'fluido_vaso': self.drp_nome_fluido.selected_value,
        'categoria': self.lbl_categoria_calculada.text
      }
    elif tipo_eq == "Caldeira":
      especificacoes = {
        'ano_fabricacao': self.num_ano_caldeira.text,
        'codigo_construcao': self.txt_cod_caldeira.text,
        'ano_edicao_codigo': self.num_edicao_caldeira.text,
        'combustivel': getattr(self, 'txt_combustivel', self).text if hasattr(self, 'txt_combustivel') else ""
      }
    elif tipo_eq == "Tanque Metálico":
      especificacoes = {
        'ano_fabricacao': self.num_ano_tanque.text,
        'codigo_construcao': self.txt_cod_tanque.text,
        'ano_edicao_codigo': self.num_edicao_tanque.text,
        'pdf_plano_inspecao': self.file_plano_tanque.file
      }
    elif "Tubulação" in tipo_eq:
      especificacoes = {
        'fluido_tub': self.drp_fluido_tubo.selected_value,
        'extensao': int(getattr(self, 'num_extensao', self).text or 0)
      }

    lista_instrumentos = []
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel:
      for row in painel.get_components():
        if isinstance(row, ItemInstrumento):
          lista_instrumentos.append({
            'tag_instrumento': row.txt_tag_inst.text,
            'tipo': row.txt_tipo_manual.text,
            'data_calibracao': row.dt_calib_inst.date,
            'prazo_calibracao': row.dt_prazo_inst.date,
            'status': "Ativo"
          })

    if dados_mestre['tag'] and dados_mestre['unidade']:
      anvil.server.call('salvar_ativo_completo', dados_mestre, especificacoes, lista_instrumentos, self.item_edicao)
      Notification("Ativo salvo e indexado com sucesso!", style="success").show()
      if not self.item_edicao: self.limpar_tela()
    else:
      alert("Os campos TAG e Unidade são obrigatórios!")

  def limpar_tela(self):
    self.txt_tag.text = ""
    self.txt_nome_operacional.text = ""
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel: painel.clear()

  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()