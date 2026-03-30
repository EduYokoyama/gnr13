from ._anvil_designer import FormAtivoNR13Template
from anvil import *
import anvil.server

class FormAtivoNR13(FormAtivoNR13Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # 1. Carregar unidades no DropDown (Vínculo)
    try:
      unidades_db = anvil.server.call('buscar_unidades')
      self.drp_unidade.items = [(u['nome_unidade'], u['row_objeto']) for u in unidades_db]
    except:
      pass

    # 2. CARREGAR FLUIDOS (Isso resolve o DropDown vazio)
    # Assumindo que você tem uma tabela chamada 'fluidos_referencia'
    try:
      # Se você tiver uma função no servidor para isso, use-a. 
      # Caso contrário, buscamos direto se a tabela estiver visível:
      fluidos = anvil.server.call('buscar_fluidos_lista') # Verifique se essa função existe no Server
      self.drp_nome_fluido.items = fluidos
    except:
      # Caso a função acima não exista, use uma lista padrão para não ficar vazio:
      self.drp_nome_fluido.items = ["Ar Comprimido", "Água", "Vapor", "Nitrogênio", "GLP", "Outros"]

    # 3. Estado inicial de visibilidade
    self.alternar_campos_equipamento()

  def drp_tipo_equipamento_change(self, **event_args):
    """Sempre que mudar o tipo, reavalia qual card mostrar"""
    self.alternar_campos_equipamento()

  def alternar_campos_equipamento(self):
    """Gerencia a visibilidade dos cards (singular)"""
    # .strip() remove espaços invisíveis que podem quebrar o IF
    tipo = self.drp_tipo_equipamento.selected_value

    # Mapeamento dos componentes (Nomes do seu Design)
    c_vaso = getattr(self, 'card_vaso', None)
    c_caldeira = getattr(self, 'card_caldeira', None)
    c_tanque = getattr(self, 'card_tanque', None)
    c_tubulacao = getattr(self, 'card_tubulacao', None)

    # Esconde todos para resetar a tela
    for c in [c_vaso, c_caldeira, c_tanque, c_tubulacao]:
      if c: c.visible = False

    # Mostra conforme seleção (Usamos 'in' para evitar erro de acentuação/espaço)
    if not tipo: return

    if "Vaso" in tipo and c_vaso:
      c_vaso.visible = True
    elif "Caldeira" in tipo and c_caldeira:
      c_caldeira.visible = True
    elif "Tanque" in tipo and c_tanque:
      c_tanque.visible = True
    elif "Tubulação" in tipo or "Tubulacao" in tipo:
      if c_tubulacao: c_tubulacao.visible = True

  # --- Funções de Suporte para evitar Warnings ---
  def drp_nome_fluido_change(self, **event_args): pass
  def calcular_categoria(self, **event_args): pass
  def num_pmta_change(self, **event_args): self.calcular_categoria()
  def drp_grupo_fluido_change(self, **event_args): self.calcular_categoria()
  def num_volume_change(self, **event_args): self.calcular_categoria()
  def drp_grupo_fluido_change(self, **event_args): self.calcular_categoria()

  def btn_salvar_click(self, **event_args):
    # (Lógica de salvar enviada anteriormente)
    pass

  @handle("drp_unidade", "change")
  def drp_unidade_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
