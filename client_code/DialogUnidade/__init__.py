from ._anvil_designer import DialogUnidadeTemplate
from anvil import *
import anvil.server
import anvil.http

class DialogUnidade(DialogUnidadeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.drp_estado.items = [("Acre", "AC"), ("São Paulo", "SP"), ("Minas Gerais", "MG"), ("Rio de Janeiro", "RJ"), ("Paraná", "PR")] # Encurtado para exemplo, pode manter os seus
    self.drp_estado.placeholder = "Selecione o Estado"

  def buscar_cep_e_coords(self):
    cep_limpo = self.txt_cep.text.replace("-", "").replace(".", "").strip()
    if len(cep_limpo) == 8:
      try:
        res = anvil.http.request(f"https://viacep.com.br/ws/{cep_limpo}/json/", json=True)
        if "erro" not in res:
          self.txt_endereco.text = res.get('logradouro', '')
          self.txt_cidade.text = res.get('localidade', '')
          self.drp_estado.selected_value = res.get('uf', '')
      except: pass

  @handle("txt_cep", "lost_focus")
  def txt_cep_lost_focus(self, **event_args): self.buscar_cep_e_coords()
  @handle("txt_cep", "pressed_enter")
  def txt_cep_pressed_enter(self, **event_args): self.buscar_cep_e_coords()