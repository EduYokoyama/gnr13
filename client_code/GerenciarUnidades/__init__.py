from ._anvil_designer import GerenciarUnidadesTemplate
from anvil import *
import anvil.server

class GerenciarUnidades(GerenciarUnidadesTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.atualizar_lista()

  def atualizar_lista(self):
    """Chama o servidor para pegar a lista com as contagens atualizadas"""
    self.repeating_panel_unidades.items = anvil.server.call('buscar_unidades')

  def btn_nova_unidade_click(self, **event_args):
    """Abre o diálogo de cadastro de unidade"""
    from ..DialogUnidade import DialogUnidade
    edicao_form = DialogUnidade()

    save_clicked = alert(
      content=edicao_form,
      title="Cadastrar Nova Unidade Fabril",
      large=True,
      buttons=[("Salvar", True), ("Cancelar", False)]
    )

    if save_clicked:
      novos_dados = {
        'nome': edicao_form.txt_nome.text,
        'cidade': edicao_form.txt_cidade.text,
        'estado': edicao_form.drp_estado.selected_value,
        'endereco': edicao_form.txt_endereco.text,
        'cep': edicao_form.txt_cep.text,
        'telefone': edicao_form.txt_telefone.text,
        'lat_long': edicao_form.txt_lat_long.text
      }

      if novos_dados['nome'] and novos_dados['estado']:
        anvil.server.call('salvar_unidade', novos_dados)
        self.atualizar_lista()
        Notification("Unidade salva com sucesso!", style="success").show()
      else:
        alert("Nome e Estado são obrigatórios!")