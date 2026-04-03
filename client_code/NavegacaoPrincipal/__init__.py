from ._anvil_designer import NavegacaoPrincipalTemplate
from anvil import *
import anvil.server

class NavegacaoPrincipal(NavegacaoPrincipalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Abre a tela inicial
    self.lnk_dashboard_click()

  def abrir_tela(self, novo_form):
    self.conteudo_painel.clear()
    self.conteudo_painel.add_component(novo_form)

  def lnk_dashboard_click(self, **event_args):
    # Importação com GNR13 - a única que o seu Anvil aceitou!
    from GNR13.Dashboard import Dashboard
    self.abrir_tela(Dashboard())

  def lnk_cadastro_click(self, **event_args):
    from GNR13.FormAtivoNR13 import FormAtivoNR13
    self.abrir_tela(FormAtivoNR13())

  def lnk_unidades_click(self, **event_args):
    from GNR13.GerenciarUnidades import GerenciarUnidades
    self.abrir_tela(GerenciarUnidades())

  def lnk_inventario_click(self, **event_args):
    from GNR13.GerenciarAtivos import GerenciarAtivos
    self.abrir_tela(GerenciarAtivos())

  def lnk_sair_click(self, **event_args):
    if confirm("Deseja sair do sistema?"):
      pass