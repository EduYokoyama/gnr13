from ._anvil_designer import GerenciarInstrumentosTemplate
from anvil import *
import anvil.server

class GerenciarInstrumentos(GerenciarInstrumentosTemplate):
  def __init__(self, ativo_pai=None, **properties):
    self.init_components(**properties)
    # Guarda a referência do Vaso/Caldeira que foi passado pelo Form principal
    self.ativo_pai = ativo_pai 

    # Atualiza a lista assim que a tela abre
    if self.ativo_pai:
      self.atualizar_lista()

  def atualizar_lista(self):
    """Busca no servidor apenas os instrumentos vinculados a este ativo"""
    if not self.ativo_pai: return

    exibir_historico = self.chk_historico.checked if hasattr(self, 'chk_historico') else False
    self.rp_instrumentos.items = anvil.server.call('buscar_instrumentos_por_ativo', self.ativo_pai, exibir_historico)

  def chk_historico_change(self, **event_args):
    self.atualizar_lista()

  def btn_novo_click(self, **event_args):
    """Abre o formulário para cadastrar uma peça nova"""
    from GNR13.ItemInstrumento import ItemInstrumento

    # Instancia o formulário
    novo_inst_form = ItemInstrumento()

    # Esconde o botão "Remover" do formulário antigo
    if hasattr(novo_inst_form, 'btn_remover'):
      novo_inst_form.btn_remover.visible = False

    # Abre o form como um alerta modal
    if alert(content=novo_inst_form, title="Novo Instrumento de Segurança", buttons=[("Salvar", True), ("Cancelar", False)], large=True):

      # Lógica para pegar o tipo
      tipo_escolhido = novo_inst_form.drp_tipo_inst.selected_value
      if tipo_escolhido == "(Outro / Escrever...)":
        tipo_escolhido = novo_inst_form.txt_tipo_manual.text

      # Coleta os dados preenchidos
      dados = {
        'tag_instrumento': novo_inst_form.txt_tag_inst.text,
        'tipo': tipo_escolhido,
        'data_calibracao': getattr(novo_inst_form.dt_calib_inst, 'date', None),
        'prazo_calibracao': getattr(novo_inst_form.dt_prazo_inst, 'date', None),
        'num_serie': getattr(novo_inst_form.txt_serie_inst, 'text', None),
        'ano_fabricacao': int(novo_inst_form.txt_ano_fab_inst.text) if getattr(novo_inst_form.txt_ano_fab_inst, 'text', None) else None,
        'certificado_pdf': getattr(novo_inst_form.file_cert_inst, 'file', None) if hasattr(novo_inst_form, 'file_cert_inst') else None
      }

      if dados['tag_instrumento']:
        # Salva na base de dados atrelado ao ativo pai
        anvil.server.call('adicionar_novo_instrumento', self.ativo_pai, dados)
        Notification("Instrumento adicionado com sucesso!", style="success").show()

        # ---> ETAPA 2 ESTÁ AQUI: Atualiza a lista na tela <---
        self.atualizar_lista()
      else:
        alert("Operação cancelada: O TAG do instrumento é obrigatório.")