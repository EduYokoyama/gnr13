from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    # Inicializa os componentes físicos do formulário
    self.init_components(**properties)

    # Carrega as Unidades do banco de dados no DropDown
    try:
      unidades = app_tables.unidades.search()
      if list(unidades):
        self.drp_unidade.items = [(u['nome_unidade'], u) for u in unidades]
      else:
        self.drp_unidade.items = [("Cadastre uma unidade primeiro", None)]
    except Exception as e:
      print(f"Erro ao carregar unidades: {e}")

  def drp_tipo_equipamento_change(self, **event_args):
    """Controla a visibilidade dos cards conforme o tipo de equipamento"""
    escolha = self.drp_tipo_equipamento.selected_value

    # Esconde todos primeiro
    self.card_vaso.visible = False
    self.card_caldeira.visible = False
    self.card_tanque.visible = False
    self.card_tubulacao.visible = False

    # Mostra apenas o card selecionado
    if escolha == 'Vaso de Pressão':
      self.card_vaso.visible = True
    elif escolha == 'Caldeira':
      self.card_caldeira.visible = True
    elif escolha == 'Tanque Metálico':
      self.card_tanque.visible = True
    elif escolha == 'Sistemas de Tubulação':
      self.card_tubulacao.visible = True

  def calcular_categoria(self, **event_args):
    """Lógica de cálculo P*V e enquadramento automático na NR-13"""
    try:
      # Converte os textos para float, usando 0 se estiver vazio
      p = float(self.num_pmta.text or 0)
      v = float(self.num_volume.text or 0)
      pv = p * v

      if pv > 0:
        # Tabela simplificada de categorias
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

        self.lbl_categoria_calculada.text = f"{cat} (P.V = {pv:.2f})"
        self.lbl_categoria_calculada.foreground = "blue"
      else:
        self.lbl_categoria_calculada.text = "Aguardando dados numéricos..."
        self.lbl_categoria_calculada.foreground = "gray"
    except Exception as e:
      # Caso o usuário digite algo que não seja número
      self.lbl_categoria_calculada.text = "Erro: Verifique os valores de P e V"
      self.lbl_categoria_calculada.foreground = "red"

  def num_pmta_change(self, **event_args):
    """Acionado a cada tecla digitada no campo PMTA"""
    self.calcular_categoria()

  def num_volume_change(self, **event_args):
    """Acionado a cada tecla digitada no campo Volume"""
    self.calcular_categoria()

  def btn_salvar_click(self, **event_args):
    """Coleta os dados e envia para o Server Module para gravação definitiva"""
    print(">>> Botão salvar acionado!")

    # Validação de campos obrigatórios
    if not self.txt_tag.text or not self.drp_unidade.selected_value:
      alert("Por favor, preencha ao menos o TAG e a UNIDADE.")
      return

    try:
      # 1. Empacota Dados Comuns (Mestre)
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

      # 2. Empacota Dados Específicos (Ex: Vaso de Pressão)
      dados_specs = {}
      if dados_mestre['tipo'] == 'Vaso de Pressão':
        dados_specs = {
          'pmta': float(self.num_pmta.text or 0),
          'volume': float(self.num_volume.text or 0),
          'fluido_servico': self.drp_fluido_vaso.selected_value,
          'categoria': self.lbl_categoria_calculada.text
        }

      # 3. Chama a função no Servidor
      with Notification("Salvando no Banco de Dados..."):
        # Enviamos uma lista vazia [] para instrumentos por enquanto
        sucesso = anvil.server.call('salvar_ativo_completo', dados_mestre, dados_specs, [])

        if sucesso:
          alert("✅ Ativo cadastrado com sucesso!")
          # Limpa o formulário recarregando-o
          open_form('FormAtivoNR13')

    except Exception as e:
      alert(f"Erro ao salvar: {e}")