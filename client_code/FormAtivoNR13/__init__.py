from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    # Inicializa os componentes (Paredes do formulário)
    self.init_components(**properties)

    # Preenche o DropDown de unidades
    try:
      unidades = app_tables.unidades.search()
      if list(unidades):
        self.drp_unidade.items = [(u['nome_unidade'], u) for u in unidades]
      else:
        # Caso o banco esteja vazio, mostra o teste manual
        self.drp_unidade.items = ["Planta Norte (Teste)", "Planta Sul (Teste)"]
    except Exception as e:
      print(f"Erro ao carregar unidades: {e}")

  def drp_tipo_equipamento_change(self, **event_args):
    """Lógica de visibilidade dinâmica dos cards"""
    escolha = self.drp_tipo_equipamento.selected_value

    # Esconde todos primeiro
    self.card_vaso.visible = False
    self.card_caldeira.visible = False
    self.card_tanque.visible = False
    self.card_tubulacao.visible = False

    # Mostra o selecionado
    if escolha == 'Vaso de Pressão':
      self.card_vaso.visible = True
    elif escolha == 'Caldeira':
      self.card_caldeira.visible = True
    elif escolha == 'Tanque Metálico':
      self.card_tanque.visible = True
    elif escolha == 'Sistemas de Tubulação':
      self.card_tubulacao.visible = True

  def btn_salvar_click(self, **event_args):
    # A. Coleta Dados Comuns (Mestre)
    dados_mestre = {
      'tag': self.txt_tag.text,
      'nome_operacional': self.txt_nome_operacional.text,
      'tipo': self.drp_tipo_equipamento.selected_value,
      'unidade': self.drp_unidade.selected_value,
      'fabricante': self.txt_fabricante.text,
      'ano_fabricacao': int(self.num_ano.text) if self.num_ano.text else 0,
      'data_proxima': self.dt_proxima_insp.date,
      'pdf_prontuario': self.file_prontuario.file,
      'pdf_art': self.file_ART.file
    }

    # B. Coleta Dados Específicos
    dados_specs = {}
    tipo = dados_mestre['tipo']

    if tipo == 'Vaso de Pressão':
      dados_specs = {
        'pmta': float(self.num_pmta.text or 0),
        'volume': float(self.num_volume.text or 0),
        'fluido_servico': self.drp_fluido_vaso.selected_value,
        'categoria': self.lbl_categoria_calculada.text
      }
    elif tipo == 'Caldeira':
      dados_specs = {
        'cap_vapor': float(self.num_cap_vapor.text or 0),
        'sup_aquecimento': float(self.num_sup_aquecimento.text or 0),
        'combustivel': self.drp_combustivel.selected_value
      }

    # C. Lista de instrumentos
    lista_inst = self.rp_dispositivos.items 

    # D. Chamada Final ao Servidor
    with Notification("Salvando Ativo e Documentos no Cofre..."):
      sucesso = anvil.server.call('salvar_ativo_completo', dados_mestre, dados_specs, lista_inst)
      if sucesso:
        Notification("✅ Sucesso! Ativo cadastrado.", style="success").show()

  def calcular_categoria(self):
    """Calcula P*V e define a Categoria NR-13"""
    try:
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      pv = p * v

      # Exemplo simplificado de enquadramento NR-13 (ajuste conforme a tabela oficial)
      if pv >= 100:
        cat = "CATEGORIA I"
      elif pv >= 30:
        cat = "CATEGORIA II"
      elif pv >= 2.5:
        cat = "CATEGORIA III"
      elif pv >= 1:
        cat = "CATEGORIA IV"
      else:
        cat = "CATEGORIA V"

      if pv > 0:
        self.lbl_categoria_calculada.text = f"{cat} (P.V = {pv:.2f})"
        self.lbl_categoria_calculada.foreground = "blue"
      else:
        self.lbl_categoria_calculada.text = "Aguardando dados..."
    except:
      pass

  @handle("num_pmta", "change")
  def num_pmta_change(self, **event_args):
    """Este método é chamado quando o conteúdo da caixa de texto muda"""
    self.calcular_categoria() # <--- O 'self.' é obrigatório aqui!
    pass

  @handle("num_volume", "change")
  def num_volume_change(self, **event_args):
    """Este método é chamado quando o conteúdo da caixa de texto muda"""
    self.calcular_categoria() # <--- O 'self.' é obrigatório aqui!
    pass


