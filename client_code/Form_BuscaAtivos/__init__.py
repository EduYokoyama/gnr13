from ._anvil_designer import Form_BuscaAtivosTemplate
import anvil.server

class Form_BuscaAtivos(Form_BuscaAtivosTemplate):
  def __init__(self, ativos_ja_selecionados=None, **properties):
    self.init_components(**properties)

    # Guarda os ativos que já vieram selecionados da tela anterior (como uma lista de IDs para facilitar)
    self.selecionados = ativos_ja_selecionados if ativos_ja_selecionados is not None else []

    # Carrega a lista inicial
    self.atualizar_grid()

  def atualizar_grid(self, texto_busca=""):
    """Busca no servidor e joga para o DataGrid"""
    resultados = anvil.server.call('buscar_ativos_grid', texto_busca)
    self.grid_ativos.items = resultados

  def txt_busca_tag_change(self, **event_args):
    """Filtra a tabela conforme o usuário digita"""
    self.atualizar_grid(self.txt_busca_tag.text)

  def btn_confirmar_click(self, **event_args):
    """Fecha o pop-up (Alert) devolvendo a lista de ativos selecionados"""
    # Varremos as linhas visíveis para ver quem foi marcado/desmarcado
    # (Para sistemas grandes, a lógica de manter estado de checkbox com paginação requer um pouco mais de código, 
    # mas esta versão atende bem a visualização em tela única)

    lista_final = []
    for row in self.grid_ativos.get_components():
      # 'row' é a instância do ItemTemplate. Pegamos o checkbox dentro dele.
      chk = row.chk_selecionado
      ativo_banco_dados = row.item # A linha do banco

      if chk.checked:
        lista_final.append(ativo_banco_dados)

    # O método 'raise_event("x-close-alert")' fecha o modal e passa o valor de volta
    self.raise_event("x-close-alert", value=lista_final)