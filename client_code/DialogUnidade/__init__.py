from ._anvil_designer import DialogUnidadeTemplate
from anvil import *
import anvil.server

class DialogUnidade(DialogUnidadeTemplate):
  def __init__(self, **properties):
    # Inicializa os componentes do formulário
    self.init_components(**properties)

    # Lista de Estados Brasileiros para o DropDown
    self.drp_estado.items = [
      ("Acre", "AC"), ("Alagoas", "AL"), ("Amapá", "AP"), ("Amazonas", "AM"),
      ("Bahia", "BA"), ("Ceará", "CE"), ("Distrito Federal", "DF"), ("Espírito Santo", "ES"),
      ("Goiás", "GO"), ("Maranhão", "MA"), ("Mato Grosso", "MT"), ("Mato Grosso do Sul", "MS"),
      ("Minas Gerais", "MG"), ("Pará", "PA"), ("Paraíba", "PB"), ("Paraná", "PR"),
      ("Pernambuco", "PE"), ("Piauí", "PI"), ("Rio de Janeiro", "RJ"), ("Rio Grande do Norte", "RN"),
      ("Rio Grande do Sul", "RS"), ("Rondônia", "RO"), ("Roraima", "RR"), ("Santa Catarina", "SC"),
      ("São Paulo", "SP"), ("Sergipe", "SE"), ("Tocantins", "TO")
    ]
    self.drp_estado.placeholder = "Selecione o Estado"