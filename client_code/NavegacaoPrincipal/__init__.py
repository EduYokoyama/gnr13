from ._anvil_designer import NavegacaoPrincipalTemplate
from anvil import *
import anvil.server

class NavegacaoPrincipal(NavegacaoPrincipalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Agora a tela inicial já é o Dashboard!
    self.lnk_dashboard_click()

  def abrir_tela(self, novo_form):
    self.conteudo_painel.clear()
    self.conteudo_painel.add_component(novo_form)

  @handle("lnk_dashboard", "click")
  def lnk_dashboard_click(self, **event_args):
    """Abre a tela de Dashboard"""
    from Controle_NR_13.Dashboard import Dashboard
    self.abrir_tela(Dashboard())

  @handle("lnk_cadastro", "click")
  def lnk_cadastro_click(self, **event_args):
    from Controle_NR_13.FormAtivoNR13 import FormAtivoNR13
    self.abrir_tela(FormAtivoNR13())

  @handle("lnk_unidades", "click")
  def lnk_unidades_click(self, **event_args):
    from Controle_NR_13.GerenciarUnidades import GerenciarUnidades
    self.abrir_tela(GerenciarUnidades())

  @handle("lnk_sair", "click")
  def lnk_sair_click(self, **event_args):
    if confirm("Deseja sair?"):
      pass