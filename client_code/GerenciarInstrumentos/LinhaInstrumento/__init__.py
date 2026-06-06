from ._anvil_designer import LinhaInstrumentoTemplate
from anvil import *
import anvil.server
import datetime

class LinhaInstrumento(LinhaInstrumentoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # --- LIGAÇÃO DOS DADOS (DATA BINDING VIA CÓDIGO) ---
    if self.item:
      self.lbl_tag.text = self.item.get('tag_instrumento', 'S/ TAG')
      self.lbl_tipo.text = self.item.get('tipo', '')

      status = self.item.get('status', 'Ativo')
      if status == "Substituído" or status == "Inativo":
        self.lbl_vencimento.visible = False
        self.dt_substituicao.visible = True
        self.dt_substituicao.date = self.item.get('data_substituicao')
        self.btn_substituir.visible = False
        
        # Estilo visual para item desativado/inativo
        self.lbl_tag.foreground = "gray"
        self.lbl_tipo.foreground = "gray"
      else:
        self.lbl_vencimento.visible = True
        self.dt_substituicao.visible = False
        self.btn_substituir.visible = True
        
        # Verifica e formata a data para o padrão DD/MM/AAAA
        prazo = self.item.get('prazo_calibracao')
        if prazo:
          self.lbl_vencimento.text = prazo.strftime('%d/%m/%Y')
        else:
          self.lbl_vencimento.text = "N/A"

  @handle("btn_excluir", "click")
  def btn_excluir_click(self, **event_args):
    """Pergunta se deseja excluir e remove a linha se confirmado"""
    tag = self.item['tag_instrumento']

    # Exibe um alerta de confirmação
    if confirm(f"Tem a certeza que deseja remover o instrumento {tag}?"):
      # 1. Manda o servidor apagar o registo da base de dados
      anvil.server.call('remover_instrumento', self.item['row_objeto'])

      # 2. Mostra uma notificação verde de sucesso
      Notification(f"Instrumento {tag} removido.", style="success").show()

      # 3. Apaga esta linha visualmente do ecrã sem precisar recarregar tudo
      self.remove_from_parent()

  def btn_substituir_click(self, **event_args):
    """Substitui o instrumento atual por um novo"""
    from GNR13.ItemInstrumento import ItemInstrumento

    # Form para o novo instrumento
    novo_inst_form = ItemInstrumento()

    # Oculta o botão "Apagar" do form se houver
    if hasattr(novo_inst_form, 'btn_remover'):
      novo_inst_form.btn_remover.visible = False

    # Componentes para desativação do atual
    lbl_titulo_atual = Label(text=f"Desativar Instrumento Atual: {self.item['tag_instrumento']}", bold=True, foreground="red")
    lbl_data = Label(text="Data de Desativação:")
    dt_desativacao = DatePicker(date=datetime.date.today(), format="DD/MM/YYYY")
    lbl_motivo = Label(text="Motivo da Troca:")
    txt_motivo = TextBox(placeholder="Ex: Calibração vencida, falha, etc.", text="Substituição de rotina")
    
    lbl_titulo_novo = Label(text="Cadastro do Novo Instrumento:", bold=True, spacing_above="medium")

    # Container de layout
    painel_alert = ColumnPanel()
    painel_alert.add_component(lbl_titulo_atual)
    
    # Grid/Flow para data e motivo
    flow_desativacao = FlowPanel()
    flow_desativacao.add_component(lbl_data)
    flow_desativacao.add_component(dt_desativacao)
    flow_desativacao.add_component(lbl_motivo)
    flow_desativacao.add_component(txt_motivo)
    
    painel_alert.add_component(flow_desativacao)
    painel_alert.add_component(lbl_titulo_novo)
    painel_alert.add_component(novo_inst_form)

    # Abre o alert dialog
    if alert(content=painel_alert, title=f"Substituir Instrumento - {self.item['tag_instrumento']}", buttons=[("Confirmar", True), ("Cancelar", False)], large=True):
      
      # Validações e coleta de dados do novo instrumento
      tipo_escolhido = novo_inst_form.drp_tipo_inst.selected_value
      if tipo_escolhido == "(Outro / Escrever...)":
        tipo_escolhido = novo_inst_form.txt_tipo_manual.text

      tag_novo = novo_inst_form.txt_tag_inst.text
      if not tag_novo:
        alert("Substituição cancelada: O TAG do novo instrumento é obrigatório.")
        return

      dados_novo = {
        'tag_instrumento': tag_novo,
        'tipo': tipo_escolhido,
        'data_calibracao': getattr(novo_inst_form.dt_calib_inst, 'date', None),
        'prazo_calibracao': getattr(novo_inst_form.dt_prazo_inst, 'date', None),
        'num_serie': getattr(novo_inst_form.txt_serie_inst, 'text', None),
        'ano_fabricacao': int(novo_inst_form.txt_ano_fab_inst.text) if getattr(novo_inst_form.txt_ano_fab_inst, 'text', None) else None,
        'certificado_pdf': getattr(novo_inst_form.file_cert_inst, 'file', None) if hasattr(novo_inst_form, 'file_cert_inst') else None,
        'motivo_troca': txt_motivo.text
      }

      data_desat = dt_desativacao.date or datetime.date.today()

      # Executa a substituição via servidor
      anvil.server.call('executar_substituicao_instrumento', self.item['row_objeto'], dados_novo, data_desat)
      Notification("Instrumento substituído com sucesso!", style="success").show()

      # Atualiza a lista da tela principal
      self.parent.parent.parent.atualizar_lista()

  def dt_substituicao_change(self, **event_args):
    """Atualiza a data de desativação/substituição no banco de dados"""
    nova_data = self.dt_substituicao.date
    if nova_data:
      anvil.server.call('atualizar_data_substituicao', self.item['row_objeto'], nova_data)
      Notification("Data de desativação atualizada!", style="success").show()