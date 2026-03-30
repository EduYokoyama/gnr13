from ._anvil_designer import DialogUnidadeTemplate
from anvil import *
import anvil.server
import anvil.http

class DialogUnidade(DialogUnidadeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

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

  def buscar_cep_e_coords(self):
    cep_limpo = self.txt_cep.text.replace("-", "").replace(".", "").strip()
    if len(cep_limpo) == 8:
      try:
        # Busca Endereço
        res = anvil.http.request(f"https://viacep.com.br/ws/{cep_limpo}/json/", json=True)
        if "erro" not in res:
          self.txt_endereco.text = res.get('logradouro', '')
          self.txt_cidade.text = res.get('localidade', '')
          self.drp_estado.selected_value = res.get('uf', '')

          # Busca Lat/Long (Nominatim)
          query = f"{self.txt_endereco.text}, {self.txt_cidade.text}, {self.drp_estado.selected_value}, Brasil"
          geo_res = anvil.http.request(f"https://nominatim.openstreetmap.org/search?format=json&q={query}&limit=1", json=True)
          if geo_res:
            self.txt_lat_long.text = f"{geo_res[0].get('lat')}, {geo_res[0].get('lon')}"
      except:
        pass

  @handle("txt_cep", "lost_focus")
  def txt_cep_lost_focus(self, **event_args): self.buscar_cep_e_coords()
  @handle("txt_cep", "pressed_enter")
  def txt_cep_pressed_enter(self, **event_args): self.buscar_cep_e_coords()