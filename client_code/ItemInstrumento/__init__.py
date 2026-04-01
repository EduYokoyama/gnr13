from ._anvil_designer import ItemInstrumentoTemplate
from anvil import *
import anvil.server

class ItemInstrumento(ItemInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Lista técnica para Vasos de Pressão e Caldeiras
    self.lista_sugestoes = [
      "Válvula de Segurança (PSV)",
      "Manômetro",
      "Pressostato",
      "Termostato",
      "Disco de Ruptura",
      "Transmissor de Pressão",
      "Transdutor de Pressão",
      "Termopar / PT-100",
      "Manovacuômetro",
      "Válvula de Alívio",
      "Sensor de Nível / Garrafa",
      "Fluxostato",
      "Vacuômetro"
    ]

    # Define os itens do DropDown (Name: drp_tipo_inst)
    self.drp_tipo_inst.items = ["(Outro / Escrever...)"] + sorted(self.lista_sugestoes)

  def drp_tipo_inst_change(self, **event_args):
    """Quando o Dropdown muda, atualiza o texto e esconde/mostra o campo manual"""
    escolha = self.drp_tipo_inst.selected_value

    if escolha == "(Outro / Escrever...)":
      self.txt_tipo_manual.visible = True
      self.txt_tipo_manual.text = "" # Limpa para o usuário digitar
      self.txt_tipo_manual.focus()
    else:
      self.txt_tipo_manual.visible = False
      self.txt_tipo_manual.text = escolha # O texto assume o valor do Dropdown

  def txt_tipo_manual_change(self, **event_args):
    """Se o usuário digitar manualmente, resetamos o Dropdown para '(Outro)'"""
    if self.txt_tipo_manual.text != "":
      if self.drp_tipo_inst.selected_value != "(Outro / Escrever...)":
        self.drp_tipo_inst.selected_value = "(Outro / Escrever...)"

  def btn_remover_click(self, **event_args):
    """Remove esta linha do painel pai"""
    self.remove_from_parent()