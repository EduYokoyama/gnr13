from GNR13.DialogUnidade import DialogUnidade # Importação absoluta corrigida [4]
from ._anvil_designer import GerenciarUnidadesTemplate
from anvil import *
import anvil.server

class GerenciarUnidades(GerenciarUnidadesTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.atualizar_lista()

  def atualizar_lista(self):
    self.repeating_panel_unidades.items = anvil.server.call('buscar_unidades')

  def btn_nova_unidade_click(self, **event_args):
    edicao_form = DialogUnidade()
    save_clicked = alert(content=edicao_form, title="Cadastrar Nova Unidade Fabril", large=True, buttons=[("Salvar", True), ("Cancelar", False)])

    if save_clicked:
      # Chaves corrigidas para bater com a Data Table [1]
      novos_dados = {
        'nome_unidade': edicao_form.txt_nome.text, 
        'cidade': edicao_form.txt_cidade.text,
        'estado': edicao_form.drp_estado.selected_value, 
        'endereco_unidade': edicao_form.txt_endereco.text,
        'cep': edicao_form.txt_cep.text, 
        'telefone': edicao_form.txt_telefone.text,
        'lat_long': edicao_form.txt_lat_long.text
      }

      if novos_dados['nome_unidade'] and novos_dados['estado']:
        anvil.server.call('salvar_unidade', novos_dados)
        self.atualizar_lista()
        Notification("Unidade salva com sucesso!", style="success").show()
      else:
        alert("Nome da Unidade e Estado são obrigatórios!")