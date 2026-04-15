from ._anvil_designer import Form_BuscaAtivosTemplate
from anvil import *
import anvil.server

class Form_BuscaAtivos(Form_BuscaAtivosTemplate):
  def __init__(self, ativos_ja_selecionados=None, **properties):
    self.init_components(**properties)

    # Guarda os ativos que já vieram selecionados da tela anterior
    self.selecionados = ativos_ja_selecionados if ativos_ja_selecionados is not None else []

    # Carrega a lista inicial assim que a tela abre
    self.atualizar_grid()

  def atualizar_grid(self, texto_busca=""):
    """Busca no servidor e joga para o painel de repetição (linhas)"""
    resultados = anvil.server.call('buscar_ativos_grid', texto_busca)

    # Usando o nome padrão do Anvil para as linhas da tabela
    self.repeating_panel_1.items = resultados

  def txt_busca_tag_change(self, **event_args):
    """Filtra a tabela conforme o usuário digita"""
    self.atualizar_grid(self.txt_busca_tag.text)

  def btn_confirmar_click(self, **event_args):
    """Fecha o pop-up devolvendo a lista de ativos selecionados"""
    lista_final = []

    # Varre as linhas visíveis usando o repeating_panel_1
    for row in self.repeating_panel_1.get_components():
      # Pega o checkbox e a linha do banco de dados correspondente
      chk = row.chk_selecionado
      ativo_banco_dados = row.item 

      if chk.checked:
        lista_final.append(ativo_banco_dados)

    # Fecha a janela modal e envia os dados de volta para o form principal
    self.raise_event("x-close-alert", value=lista_final)