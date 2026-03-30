from ._anvil_designer import DialogUnidadeTemplate
from anvil import *
import anvil.server
import anvil.google.maps

class DialogUnidade(DialogUnidadeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # 1. Configura os Estados
    self.drp_estado.items = [
      ("Acre", "AC"), ("Alagoas", "AL"), ("Amapá", "AP"), ("Amazonas", "AM"),
      ("Bahia", "BA"), ("Ceará", "CE"), ("Distrito Federal", "DF"), ("Espírito Santo", "ES"),
      ("Goiás", "GO"), ("Maranhão", "MA"), ("Mato Grosso", "MT"), ("Mato Grosso do Sul", "MS"),
      ("Minas Gerais", "MG"), ("Pará", "PA"), ("Paraíba", "PB"), ("Paraná", "PR"),
      ("Pernambuco", "PE"), ("Piauí", "PI"), ("Rio de Janeiro", "RJ"), ("Rio Grande do Norte", "RN"),
      ("Rio Grande do Sul", "RS"), ("Rondônia", "RO"), ("Roraima", "RR"), ("Santa Catarina", "SC"),
      ("São Paulo", "SP"), ("Sergipe", "SE"), ("Tocantins", "TO")
    ]

    # 2. Configura o Mapa (Centro inicial no Brasil)
    self.mapa_unidade.center = anvil.google.maps.LatLng(-14.235, -51.925)
    self.mapa_unidade.zoom = 4

    # 3. Adiciona um marcador arrastável
    self.marker = anvil.google.maps.Marker(
      position=self.mapa_unidade.center,
      draggable=True,
      title="Arraste até a localização da unidade"
    )
    self.mapa_unidade.add_component(self.marker)

    # Variável interna para salvar a posição
    self.lat_long_final = f"{self.marker.position.lat()}, {self.marker.position.lng()}"

  def mapa_unidade_click(self, lat_lng, **event_args):
    """Se o usuário clicar em qualquer lugar do mapa, o marcador pula para lá"""
    self.marker.position = lat_lng
    self.lat_long_final = f"{lat_lng.lat()}, {lat_lng.lng()}"