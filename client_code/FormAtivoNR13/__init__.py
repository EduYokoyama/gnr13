from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # 1. Carrega as Unidades
    try:
      unidades = app_tables.unidades.search()
      self.drp_unidade.items = [(u['nome_unidade'], u) for u in unidades if u['nome_unidade']]
    except:
      pass

    # 2. Carrega os Fluidos da NR-13 (Com correção para evitar erro de None)
    try:
      todos_os_fluidos = app_tables.fluidos_referencia.search()

      # Filtramos apenas linhas que realmente tenham um nome preenchido
      lista_fluidos = [(f['nome_fluido'], f) for f in todos_os_fluidos if f['nome_fluido'] is not None]

      if lista_fluidos:
        # Ordena a lista alfabeticamente pelo nome
        lista_fluidos.sort(key=lambda x: x[0])
        self.drp_nome_fluido.items = lista_fluidos
      else:
        self.drp_nome_fluido.items = [("Nenhum fluido cadastrado", None)]

    except Exception as e:
      print(f"Erro ao carregar lista de fluidos: {e}")

  def drp_tipo_equipamento_change(self, **event_args):
    """Controla a visibilidade dos cards técnicos"""
    escolha = self.drp_tipo_equipamento.selected_value
    self.card_vaso.visible = (escolha == 'Vaso de Pressão')
    self.card_caldeira.visible = (escolha == 'Caldeira')
    self.card_tanque.visible = (escolha == 'Tanque Metálico')
    self.card_tubulacao.visible = (escolha == 'Sistemas de Tubulação')

  def drp_nome_fluido_change(self, **event_args):
    """Preenche grupo e comentário automaticamente"""
    f = self.drp_nome_fluido.selected_value
    if f:
      self.drp_grupo_fluido.selected_value = f['grupo_nr13']
      self.lbl_comentario_fluido.text = f['comentario']
      self.calcular_categoria()

  def calcular_categoria(self, **event_args):
    """Lógica da Matriz NR-13"""
    try:
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      pv = p * v
      grupo = self.drp_grupo_fluido.selected_value
      cat = "N/A"

      if pv > 0 and grupo:
        if grupo == 'Grupo A':
          cat = "CATEGORIA I" if pv >= 100 else "CATEGORIA II"
        elif grupo == 'Grupo B':
          if pv >= 100: cat = "CATEGORIA I"
          elif pv >= 30: cat = "CATEGORIA II"
          else: cat = "CATEGORIA III"
        elif grupo == 'Grupo C':
          if pv >= 100: cat = "CATEGORIA I"
          elif pv >= 30: cat = "CATEGORIA II"
          elif pv >= 2.5: cat = "CATEGORIA III"
          else: cat = "CATEGORIA IV"
        elif grupo == 'Grupo D':
          if pv >= 100: cat = "CATEGORIA II"
          elif pv >= 30: cat = "CATEGORIA III"
          elif pv >= 2.5: cat = "CATEGORIA IV"
          else: cat = "CATEGORIA V"

        self.lbl_categoria_calculada.text = f"{cat} (P.V = {pv:.2f})"
        self.lbl_categoria_calculada.foreground = "blue"
      else:
        self.lbl_categoria_calculada.text = "Aguardando dados..."
        self.lbl_categoria_calculada.foreground = "gray"
    except:
      pass

  def num_pmta_change(self, **event_args):
    self.calcular_categoria()

  def num_volume_change(self, **event_args):
    self.calcular_categoria()

  def btn_salvar_click(self, **event_args):
    """Salva o ativo no banco de dados"""
    if not self.txt_tag.text or not self.drp_unidade.selected_value:
      alert("TAG e UNIDADE são obrigatórios.")
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
      with Notification("Salvando..."):
        res = anvil.server.call('salvar_ativo_completo', dados_mestre, dados_specs, [])
        if res:
          alert("✅ Ativo cadastrado!")
          open_form('FormAtivoNR13')
    except Exception as e:
      alert(f"Erro ao salvar: {e}")