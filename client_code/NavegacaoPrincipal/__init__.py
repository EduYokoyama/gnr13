from ._anvil_designer import NavegacaoPrincipalTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class NavegacaoPrincipal(NavegacaoPrincipalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.conteudo_painel.clear()
    self.conteudo_painel.add_component(Label(text="Bem-vindo ao Sistema Controle NR-13! Selecione uma opção no menu lateral."))

  def abrir_tela(self, novo_form):
    self.conteudo_painel.clear()
    self.conteudo_painel.add_component(novo_form)

  @handle("lnk_cadastro", "click")
  def lnk_cadastro_click(self, **event_args):
    # Importação pelo caminho completo do seu projeto
    from Controle_NR_13.FormAtivoNR13 import FormAtivoNR13
    self.abrir_tela(FormAtivoNR13())

  @handle("lnk_unidades", "click")
  def lnk_unidades_click(self, **event_args):
    # Importação pelo caminho completo do seu projeto
    from Controle_NR_13.GerenciarUnidades import GerenciarUnidades
    self.abrir_tela(GerenciarUnidades())

  @handle("lnk_dashboard", "click")
  def lnk_dashboard_click(self, **event_args):
    self.abrir_tela(Label(text="Dashboard em construção..."))

  @handle("lnk_sair", "click")
  def lnk_sair_click(self, **event_args):
    if confirm("Deseja sair?"):
      pass