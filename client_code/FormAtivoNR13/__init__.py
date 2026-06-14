from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from GNR13.Form_BuscaAtivos import Form_BuscaAtivos

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, item_edicao=None, **properties):
    self.init_components(**properties)
    self.item_edicao = item_edicao
    self.lista_ativos_conectados = [] # Inicializa a lista vazia

    # --- CARREGAMENTO INICIAL DE DADOS ---
    try:
      unidades = anvil.server.call('buscar_unidades')
      self.drp_unidade.items = [(u['nome_unidade'], u['row_objeto']) for u in unidades]

      fluidos = anvil.server.call('buscar_fluidos_lista')
      self.drp_nome_fluido.items = ["Selecione..."] + fluidos
      self.drp_fluido_tubo.items = ["Selecione..."] + fluidos
      self.drp_status_prontuario.items = ["Original", "Reconstituído", "Inexistente"]
      # Busca vasos, caldeiras e tanques para o dropdown múltiplo da Tubulação
      ativos_pais = anvil.server.call('buscar_ativos_pais') 
      if hasattr(self, 'multi_ativos_ligados'):
        self.multi_ativos_ligados.items = [(f"{a['tag']} ({a['tipo']})", a) for a in ativos_pais]

      self.drp_tipo_equipamento.items = ["Vaso de Pressão", "Caldeira", "Tanque Metálico", "Sistemas de Tubulação"]
    except Exception as e:
      print(f"Erro ao inicializar formulário e buscar dados: {e}")

    # --- FLUXO DE NAVEGAÇÃO ---
    if self.item_edicao:
      self.preencher_dados_edicao()
    else:
      self.alternar_campos_equipamento()

  # --- FUNÇÕES DE PREENCHIMENTO E INTERFACE ---
  def preencher_dados_edicao(self):
    it = self.item_edicao
    self.txt_tag.text = it.get('tag')
    self.txt_nome_operacional.text = it.get('nome_operacional')
    self.txt_fabricante.text = it.get('fabricante')
    self.drp_unidade.selected_value = it.get('unidade')
    self.drp_tipo_equipamento.selected_value = it.get('tipo')

    if hasattr(self, 'drp_status_prontuario'):
      status_banco = it.get('status_prontuario')
      # Só preenche se o que veio do banco estiver na lista permitida, senão deixa em branco ou "Original"
      if status_banco in self.drp_status_prontuario.items:
        self.drp_status_prontuario.selected_value = status_banco
      else:
        self.drp_status_prontuario.selected_value = "Original" # Força um padrão válido
    if hasattr(self, 'num_ano_prontuario'):
      self.num_ano_prontuario.text = it.get('ano_prontuario')

    specs = anvil.server.call('obter_specs_ativo', it['row_objeto'])
    if specs:
      tipo = it.get('tipo')
      if tipo == "Vaso de Pressão":
        if hasattr(self, 'num_ano_vaso'): self.num_ano_vaso.text = specs.get('ano_fabricacao')
        if hasattr(self, 'txt_cod_vaso'): self.txt_cod_vaso.text = specs.get('codigo_construcao')
        if hasattr(self, 'num_pmta'): self.num_pmta.text = specs.get('pmta')
        if hasattr(self, 'num_volume'): self.num_volume.text = specs.get('volume')
        if hasattr(self, 'num_edicao_vaso'): self.num_edicao_vaso.text = specs.get('ano_edicao_codigo')
        self.drp_nome_fluido.selected_value = specs.get('fluido_vaso')
        self.drp_nome_fluido_change() 
      elif tipo == "Caldeira":
        if hasattr(self, 'num_ano_caldeira'): self.num_ano_caldeira.text = specs.get('ano_fabricacao')
        if hasattr(self, 'txt_cod_caldeira'): self.txt_cod_caldeira.text = specs.get('codigo_construcao')
        if hasattr(self, 'num_cap_vapor'): self.num_cap_vapor.text = specs.get('cap_vapor')
        if hasattr(self, 'num_sup_aquecimento'): self.num_sup_aquecimento.text = specs.get('sup_aquecimento')
        if hasattr(self, 'txt_combustivel'): self.txt_combustivel.text = specs.get('combustivel')
        if hasattr(self, 'num_edicao_caldeira'): self.num_edicao_caldeira.text = specs.get('ano_edicao_codigo')
      elif tipo == "Tanque Metálico":
        if hasattr(self, 'num_diametro_tanque'): self.num_diametro_tanque.text = specs.get('diametro_ext')
        # CORREÇÃO: Puxando o volume na hora de editar
        if hasattr(self, 'num_volume_tanque'): self.num_volume_tanque.text = specs.get('volume_nominal')
        if hasattr(self, 'num_ano_tanque'): self.num_ano_tanque.text = specs.get('ano_fabricacao')
        if hasattr(self, 'txt_cod_tanque'): self.txt_cod_tanque.text = specs.get('codigo_construcao')
        if hasattr(self, 'num_edicao_tanque'): self.num_edicao_tanque.text = specs.get('ano_edicao_codigo')
      elif "Tubulação" in tipo or "Sistemas" in tipo:
        self.drp_fluido_tubo.selected_value = specs.get('fluido_tub')
        self.drp_fluido_tubo_change() # Aciona o evento para atualizar a label do Grupo

        if hasattr(self, 'num_extensao'): self.num_extensao.text = specs.get('extensao')
        if hasattr(self, 'num_diametro_tubo'): self.num_diametro_tubo.text = specs.get('diametro_nominal')
        if hasattr(self, 'drp_unidade_diametro'): self.drp_unidade_diametro.selected_value = specs.get('unidade_diametro', 'Polegadas (")')
        if hasattr(self, 'num_ano_tubo'): self.num_ano_tubo.text = specs.get('ano_fabricacao')
        if hasattr(self, 'txt_cod_tubo'): self.txt_cod_tubo.text = specs.get('codigo_construcao')
        if hasattr(self, 'num_ano_edicao_tubo'): self.num_ano_edicao_tubo.text = specs.get('ano_edicao_codigo')

        if hasattr(self, 'num_pmta_tubo'): self.num_pmta_tubo.text = specs.get('pmta')
        if hasattr(self, 'num_pressao_op_tubo'): self.num_pressao_op_tubo.text = specs.get('pressao_operacao')
        if hasattr(self, 'num_temp_proj_tubo'): self.num_temp_proj_tubo.text = specs.get('temp_projeto')
        if hasattr(self, 'num_espessura_min'): self.num_espessura_min.text = specs.get('espessura_minima')
        # ---> NOVO: Lógica para os Chips na Edição <---
        ativos_salvos = specs.get('ativos_conectados')
        if ativos_salvos:
          # Converte a lista do banco para a variável local e desenha
          self.lista_ativos_conectados = list(ativos_salvos)
          self.desenhar_chips()
        else:
          self.lista_ativos_conectados = []
          if hasattr(self, 'panel_chips_ativos'): self.panel_chips_ativos.clear()

          # Recarregando o DropDown Múltiplo
        if hasattr(self, 'multi_ativos_ligados'):
          ativos_salvos = specs.get('ativos_conectados')
          if ativos_salvos:
            # No Anvil Extras, basta definir selected_items com a lista de objetos Row
            self.multi_ativos_ligados.selected_items = list(ativos_salvos)

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

  # --- EVENTOS DE FLUIDO E CÁLCULOS ---
  def drp_nome_fluido_change(self, **event_args):
    nome = self.drp_nome_fluido.selected_value
    if nome and nome != "Selecione...":
      det = anvil.server.call('obter_detalhes_fluido', nome)
      if det:
        if hasattr(self, 'txt_grupo_fluido'):
          self.txt_grupo_fluido.text = det.get('grupo', '')
        if hasattr(self, 'lbl_comentario_fluido'):
          self.lbl_comentario_fluido.text = det.get('descricao', '')
        self.calcular_categoria()

  def drp_fluido_tubo_change(self, **event_args):
    nome = self.drp_fluido_tubo.selected_value
    if nome and nome != "Selecione...":
      det = anvil.server.call('obter_detalhes_fluido', nome)
      if det:
        if hasattr(self, 'lbl_grupo_tubo'):
          self.lbl_grupo_tubo.text = det.get('grupo', '')
        if hasattr(self, 'lbl_desc_fluido_tubo'):
          self.lbl_desc_fluido_tubo.text = det.get('descricao', '')

  def calcular_categoria(self, **event_args):
    try:
      p = float(getattr(self, 'num_pmta', self).text or 0) if hasattr(self, 'num_pmta') else 0
      v = float(getattr(self, 'num_volume', self).text or 0) if hasattr(self, 'num_volume') else 0
      pv = p * v

      grupo = getattr(self, 'txt_grupo_fluido', None)
      grupo_str = grupo.text if grupo else None

      if pv <= 0 or not grupo_str: return

      if "Grupo A" in grupo_str or "Grupo B" in grupo_str:
        cat = "Categoria I" if pv >= 100 else ("Categoria II" if pv >= 30 else "Categoria III")
      else:
        if pv >= 100: cat = "Categoria I"
        elif pv >= 30: cat = "Categoria II"
        elif pv >= 2.5: cat = "Categoria III"
        elif pv >= 1: cat = "Categoria IV"
        else: cat = "Categoria V"

      if hasattr(self, 'lbl_categoria_calculada'):
        self.lbl_categoria_calculada.text = f"{cat} (P.V: {pv:.2f})"
    except: pass

  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()

  # --- EVENTOS DE INSTRUMENTAÇÃO ---

  # --- FUNÇÕES DE VALIDAÇÃO E SALVAMENTO ---
  def _parse_numero(self, texto, tipo='float'):
    try:
      if texto is None or str(texto).strip() == "": return None
      return float(texto) if tipo == 'float' else int(texto)
    except: return None

  def btn_salvar_click(self, **event_args):
    from GNR13.ItemInstrumento import ItemInstrumento
    tipo_eq = self.drp_tipo_equipamento.selected_value

    if not self.txt_tag.text or not self.drp_unidade.selected_value:
      alert("Os campos TAG e Unidade são obrigatórios para o cadastro de qualquer ativo!")
      return

    # DADOS MESTRE (Tabela Principal)
    dados_mestre = {
      'tag': self.txt_tag.text,
      'nome_operacional': self.txt_nome_operacional.text,
      'unidade': self.drp_unidade.selected_value,
      'tipo': tipo_eq,
      'fabricante': self.txt_fabricante.text,
      'pdf_prontuario': getattr(self, 'file_prontuario', self).file if hasattr(self, 'file_prontuario') else None,
      'status_prontuario': getattr(self.drp_status_prontuario, 'selected_value', None)
    }

    if hasattr(self, 'num_ano_prontuario'):
      dados_mestre['ano_prontuario'] = self._parse_numero(self.num_ano_prontuario.text, 'int')

    # ESPECIFICAÇÕES (Tabelas Relacionais)
    especificacoes = {}
    if tipo_eq == "Vaso de Pressão":
      especificacoes = {
        'fluido_vaso': self.drp_nome_fluido.selected_value,
        'ano_fabricacao': self._parse_numero(getattr(self, 'num_ano_vaso', None).text if hasattr(self, 'num_ano_vaso') else None, 'int'),
        'codigo_construcao': getattr(self, 'txt_cod_vaso', None).text if hasattr(self, 'txt_cod_vaso') else None,
        'ano_edicao_codigo': self._parse_numero(getattr(self, 'num_edicao_vaso', None).text if hasattr(self, 'num_edicao_vaso') else None, 'int'),
        'pmta': self._parse_numero(getattr(self, 'num_pmta', None).text if hasattr(self, 'num_pmta') else None, 'float'),
        'volume': self._parse_numero(getattr(self, 'num_volume', None).text if hasattr(self, 'num_volume') else None, 'float'),
        'categoria': getattr(self, 'lbl_categoria_calculada', None).text if hasattr(self, 'lbl_categoria_calculada') else None
      }
    elif tipo_eq == "Caldeira":
      especificacoes = {
        'ano_fabricacao': self._parse_numero(getattr(self, 'num_ano_caldeira', None).text if hasattr(self, 'num_ano_caldeira') else None, 'int'),
        'codigo_construcao': getattr(self, 'txt_cod_caldeira', None).text if hasattr(self, 'txt_cod_caldeira') else None,
        'ano_edicao_codigo': self._parse_numero(getattr(self, 'num_edicao_caldeira', None).text if hasattr(self, 'num_edicao_caldeira') else None, 'int'),
        'cap_vapor': self._parse_numero(getattr(self, 'num_cap_vapor', None).text if hasattr(self, 'num_cap_vapor') else None, 'float'),
        'sup_aquecimento': self._parse_numero(getattr(self, 'num_sup_aquecimento', None).text if hasattr(self, 'num_sup_aquecimento') else None, 'float'),
        'combustivel': getattr(self, 'txt_combustivel', None).text if hasattr(self, 'txt_combustivel') else ""
      }
    elif tipo_eq == "Tanque Metálico":
      # CORREÇÃO: Adicionado o volume_nominal!
      especificacoes = {
        'diametro_ext': self._parse_numero(getattr(self, 'num_diametro_tanque', None).text if hasattr(self, 'num_diametro_tanque') else None, 'float'),
        'volume_nominal': self._parse_numero(getattr(self, 'num_volume_tanque', None).text if hasattr(self, 'num_volume_tanque') else None, 'float'),
        'ano_fabricacao': self._parse_numero(getattr(self, 'num_ano_tanque', None).text if hasattr(self, 'num_ano_tanque') else None, 'int'),
        'codigo_construcao': getattr(self, 'txt_cod_tanque', None).text if hasattr(self, 'txt_cod_tanque') else None,
        'ano_edicao_codigo': self._parse_numero(getattr(self, 'num_edicao_tanque', None).text if hasattr(self, 'num_edicao_tanque') else None, 'int'),
        'pdf_plano_inspecao': getattr(self, 'file_plano_tanque', None).file if hasattr(self, 'file_plano_tanque') else None
      }
    elif "Tubulação" in tipo_eq or "Sistemas" in tipo_eq:
      especificacoes = {
        'fluido_tub': self.drp_fluido_tubo.selected_value,
        # Salva o grupo do fluido que apareceu na Label
        'grupo_fluido': getattr(self, 'lbl_grupo_tubo', None).text if hasattr(self, 'lbl_grupo_tubo') else None,

        'diametro_nominal': self._parse_numero(getattr(self, 'num_diametro_tubo', None).text if hasattr(self, 'num_diametro_tubo') else None, 'float'),
        'unidade_diametro': getattr(self, 'drp_unidade_diametro', None).selected_value if hasattr(self, 'drp_unidade_diametro') else None,
        'extensao': self._parse_numero(getattr(self, 'num_extensao', None).text if hasattr(self, 'num_extensao') else None, 'float'),
        'ano_fabricacao': self._parse_numero(getattr(self, 'num_ano_tubo', None).text if hasattr(self, 'num_ano_tubo') else None, 'int'),

        'codigo_construcao': getattr(self, 'txt_cod_tubo', None).text if hasattr(self, 'txt_cod_tubo') else None,
        'ano_edicao_codigo': self._parse_numero(getattr(self, 'num_ano_edicao_tubo', None).text if hasattr(self, 'num_ano_edicao_tubo') else None, 'int'),

        'pmta': self._parse_numero(getattr(self, 'num_pmta_tubo', None).text if hasattr(self, 'num_pmta_tubo') else None, 'float'),
        'pressao_operacao': self._parse_numero(getattr(self, 'num_pressao_op_tubo', None).text if hasattr(self, 'num_pressao_op_tubo') else None, 'float'),
        'temp_projeto': self._parse_numero(getattr(self, 'num_temp_proj_tubo', None).text if hasattr(self, 'num_temp_proj_tubo') else None, 'float'),
        'espessura_minima': self._parse_numero(getattr(self, 'num_espessura_min', None).text if hasattr(self, 'num_espessura_min') else None, 'float'),

        # ---> O Pulo do Gato: Capturando a lista de múltiplos ativos <---
        'ativos_conectados': self.lista_ativos_conectados,

        'pdf_pid': getattr(self, 'file_pid_tubo', None).file if hasattr(self, 'file_pid_tubo') else None,
        'pdf_plano_insp': getattr(self, 'file_plano_tubo', None).file if hasattr(self, 'file_plano_tubo') else None
      }

   
    # EXECUÇÃO NO SERVIDOR
    try:
      # Pega a linha real do banco de dados (se estivermos editando)
      row_real = self.item_edicao.get('row_objeto') if self.item_edicao else None

      # Envia None no lugar da lista de instrumentos
      nova_row = anvil.server.call('salvar_ativo_completo', dados_mestre, especificacoes, None, row_real)

      # Atualiza o formulário para o modo "Edição", pois o ativo agora existe no banco
      self.item_edicao = {'row_objeto': nova_row, 'tag': dados_mestre['tag']}

      Notification("Dados do Ativo salvos e sincronizados com o banco de dados!", style="success").show()

      # Se foi aberto em um Alert (Edição a partir do Gerenciar Ativos), fecha o alert.
      # Caso contrário (cadastro direto), mantém os campos visíveis.
      if event_args.get('sender'):
        if row_real:
          self.raise_event("x-close-alert")

    except Exception as e:
      alert(f"Ocorreu um erro ao comunicar com o servidor: {e}")

  def limpar_tela(self):
    self.txt_tag.text = ""
    self.txt_nome_operacional.text = ""
    if hasattr(self, 'txt_fabricante'): self.txt_fabricante.text = ""
    if hasattr(self, 'file_prontuario'): self.file_prontuario.clear()
    if hasattr(self, 'file_plano_tanque'): self.file_plano_tanque.clear()
    painel = getattr(self, 'painel_instrumentos', None) or getattr(self, 'fp_instrumentos', None)
    if painel: painel.clear()

  def btn_cancelar_click(self, **event_args):
    self.limpar_tela()
    
  def btn_buscar_ativos_click(self, **event_args):
    """Abre o modal de busca"""
    # Instanciamos a tela passando o que já está selecionado
    form_busca = Form_BuscaAtivos(ativos_ja_selecionados=self.lista_ativos_conectados)

    # O alert trava a tela até o usuário clicar em Confirmar (que dispara o x-close-alert)
    resultado = alert(content=form_busca, large=True, buttons=[])

    if resultado is not None:
      self.lista_ativos_conectados = resultado
      self.desenhar_chips()

  def desenhar_chips(self):
    """Limpa o FlowPanel e cria um botãozinho (Chip) para cada ativo"""
    self.panel_chips_ativos.clear()

    for ativo in self.lista_ativos_conectados:
      # Cria um botão para atuar como uma 'Tag' visual
      chip = Button(
        text=f"{ativo['tag']} ✖", 
        role="primary-color", 
        tooltip="Clique para remover",
        spacing_above="small", 
        spacing_below="small"
      )
      # Guardamos a referência da linha do banco no próprio botão para saber quem remover depois
      chip.tag = ativo 
      chip.add_event_handler('click', self.remover_chip)

      self.panel_chips_ativos.add_component(chip)

  def remover_chip(self, **event_args):
    """Remove o ativo da lista se o usuário clicar no 'X' do chip"""
    botao_clicado = event_args['sender']
    ativo_para_remover = botao_clicado.tag

    self.lista_ativos_conectados.remove(ativo_para_remover)
    self.desenhar_chips() # Redesenha a tela

  def btn_gerenciar_inspecoes_click(self, **event_args):
    """Lógica inteligente: Salva o ativo pai antes de abrir as inspeções"""
    if not self.item_edicao or not self.item_edicao.get('row_objeto'):
      if confirm("O ativo precisa ser salvo no banco de dados primeiro. Deseja salvar e continuar?"):
        self.btn_salvar_click(sender=None) 
        if not self.item_edicao or not self.item_edicao.get('row_objeto'):
          return 
      else:
        return 

    from GNR13.GerenciarInspecoes import GerenciarInspecoes
    ativo_ref = self.item_edicao['row_objeto']
    form_insp = GerenciarInspecoes(ativo_pai=ativo_ref)
    alert(content=form_insp, large=True, title=f"Gerenciar Inspeções - {self.txt_tag.text}", buttons=[("Fechar", True)])

  def btn_gerenciar_instrumentos_click(self, **event_args):
    """This method is called when the button is clicked"""
    """Lógica inteligente: Salva o ativo pai antes de abrir os instrumentos"""
  
    # 1. Verifica se o Ativo principal já existe no banco
    if not self.item_edicao or not self.item_edicao.get('row_objeto'):
      if confirm("O ativo precisa ser salvo no banco de dados primeiro. Deseja salvar e continuar?"):

        # Chama a função de salvar, passando 'sender=None' para a tela não fechar!
        self.btn_salvar_click(sender=None) 

        # ---> CORREÇÃO 1: Verificação segura para evitar o erro de NoneType <---
        if not self.item_edicao or not self.item_edicao.get('row_objeto'):
          return 
      else:
        return # Usuário não quis salvar, aborta a operação

    # 2. Agora garantimos que o ativo pai existe. Vamos abrir o Pop-up!
    from GNR13.GerenciarInstrumentos import GerenciarInstrumentos

    ativo_ref = self.item_edicao['row_objeto']

    # Passamos o ativo pai para a nova tela filtrar os instrumentos corretamente
    form_inst = GerenciarInstrumentos(ativo_pai=ativo_ref)

    # ---> CORREÇÃO 2: Adicionado o botão [("Fechar", True)] para destravar a tela <---
    alert(content=form_inst, large=True, title=f"Gerenciar Instrumentos - {self.txt_tag.text}", buttons=[("Fechar", True)])