from ._anvil_designer import LinhaInstrumentoGeralTemplate
from anvil import *
import anvil.server
import datetime
from GNR13.ItemInstrumento import ItemInstrumento

class LinhaInstrumentoGeral(LinhaInstrumentoGeralTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    if self.item:
      self.lbl_tag.text = self.item.get('tag_instrumento', 'S/ TAG')
      self.lbl_tipo.text = self.item.get('tipo', '')
      self.lbl_ativo.text = f"{self.item.get('ativo_tag', 'S/ Ativo')} ({self.item.get('ativo_tipo', '')})"
      self.lbl_unidade.text = self.item.get('unidade_nome', '')
      
      status = self.item.get('status', 'Ativo')
      self.lbl_status.text = status
      if status == "Substituído":
        self.lbl_status.foreground = "gray"
        self.lbl_status.text = self.item.get('substituido_por_info', 'Substituído')
        self.btn_substituir.visible = False
        self.btn_calibrar.visible = False
        # Gray out tags
        self.lbl_tag.foreground = "gray"
      elif status == "Inativo":
        self.lbl_status.foreground = "red"
        self.btn_substituir.visible = True
        self.btn_calibrar.visible = True
      else:
        self.lbl_status.foreground = "green"
        self.btn_substituir.visible = True
        self.btn_calibrar.visible = True

      # Prazo Calibração
      prazo = self.item.get('prazo_calibracao')
      if prazo:
        self.lbl_prazo.text = prazo.strftime('%d/%m/%Y')
        # Check if expired
        if prazo < datetime.date.today() and status == "Ativo":
          self.lbl_prazo.foreground = "red"
          self.lbl_prazo.bold = True
        else:
          self.lbl_prazo.foreground = "black"
      else:
        self.lbl_prazo.text = "N/A"

      # Conformidade do Ativo
      self.lbl_apto.text = self.item.get('ativo_apto_instrumentos', '')
      if self.item.get('ativo_apto_bool', False):
        self.lbl_apto.foreground = "green"
      else:
        self.lbl_apto.foreground = "red"

  @handle("btn_editar", "click")
  def btn_editar_click(self, **event_args):
    """Edita os dados cadastrais do instrumento"""
    form_edicao = ItemInstrumento()
    
    # Preenche o formulário com dados existentes
    form_edicao.txt_tag_inst.text = self.item.get('tag_instrumento', '')
    form_edicao.txt_serie_inst.text = self.item.get('num_serie', '')
    form_edicao.txt_ano_fab_inst.text = str(self.item.get('ano_fabricacao', '')) if self.item.get('ano_fabricacao') else ""
    
    # Lógica de seleção do tipo no dropdown
    tipo_atual = self.item.get('tipo', '')
    if tipo_atual in form_edicao.drp_tipo_inst.items:
      form_edicao.drp_tipo_inst.selected_value = tipo_atual
      form_edicao.txt_tipo_manual.visible = False
      form_edicao.txt_tipo_manual.text = tipo_atual
    else:
      form_edicao.drp_tipo_inst.selected_value = "(Outro / Escrever...)"
      form_edicao.txt_tipo_manual.visible = True
      form_edicao.txt_tipo_manual.text = tipo_atual

    # Oculta campos de calibração para edição cadastral simples
    if hasattr(form_edicao, 'lbl_calib_titulo'): form_edicao.lbl_calib_titulo.visible = False
    form_edicao.dt_calib_inst.visible = False
    form_edicao.dt_prazo_inst.visible = False
    form_edicao.file_cert_inst.visible = False
    form_edicao.btn_ver_cert.visible = False
    
    # Oculta o botão de remover
    if hasattr(form_edicao, 'btn_remover'):
      form_edicao.btn_remover.visible = False

    if alert(content=form_edicao, title="Editar Cadastro do Instrumento", buttons=[("Salvar", True), ("Cancelar", False)], large=True):
      tipo_escolhido = form_edicao.drp_tipo_inst.selected_value
      if tipo_escolhido == "(Outro / Escrever...)":
        tipo_escolhido = form_edicao.txt_tipo_manual.text

      dados = {
        'tag_instrumento': form_edicao.txt_tag_inst.text,
        'tipo': tipo_escolhido,
        'num_serie': form_edicao.txt_serie_inst.text,
        'ano_fabricacao': int(form_edicao.txt_ano_fab_inst.text) if form_edicao.txt_ano_fab_inst.text else None
      }

      if dados['tag_instrumento']:
        anvil.server.call('editar_instrumento_geral', self.item['row_objeto'], dados)
        Notification("Instrumento atualizado com sucesso!", style="success").show()
        self.parent.parent.parent.atualizar_lista()
      else:
        alert("O TAG do instrumento é obrigatório.")

  @handle("btn_calibrar", "click")
  def btn_calibrar_click(self, **event_args):
    """Abre um formulário simples de calibração"""
    lbl_desc = Label(text=f"Registrar Calibração para {self.item['tag_instrumento']}", bold=True)
    lbl_data = Label(text="Data de Calibração:")
    dt_calib = DatePicker(date=self.item.get('data_calibracao') or datetime.date.today(), format="DD/MM/YYYY")
    lbl_prazo = Label(text="Prazo de Vencimento da Calibração:")
    dt_prazo = DatePicker(date=self.item.get('prazo_calibracao') or (datetime.date.today() + datetime.timedelta(days=365)), format="DD/MM/YYYY")
    
    lbl_cert = Label(text="PDF do Certificado:")
    file_cert = FileLoader(file_types=".pdf")
    
    # Container
    p = ColumnPanel()
    p.add_component(lbl_desc)
    
    fp1 = FlowPanel()
    fp1.add_component(lbl_data)
    fp1.add_component(dt_calib)
    p.add_component(fp1)
    
    fp2 = FlowPanel()
    fp2.add_component(lbl_prazo)
    fp2.add_component(dt_prazo)
    p.add_component(fp2)
    
    fp3 = FlowPanel()
    fp3.add_component(lbl_cert)
    fp3.add_component(file_cert)
    p.add_component(fp3)

    if alert(content=p, title="Nova Calibração", buttons=[("Salvar Calibração", True), ("Cancelar", False)]):
      pdf = file_cert.file
      if pdf:
        nome = getattr(pdf, 'name', '') or ''
        if not nome.lower().endswith('.pdf'):
          alert("O certificado deve ser um arquivo PDF.")
          return
          
      anvil.server.call(
        'registrar_calibracao_instrumento',
        self.item['row_objeto'],
        dt_calib.date,
        dt_prazo.date,
        pdf
      )
      Notification("Calibração registrada com sucesso!", style="success").show()
      self.parent.parent.parent.atualizar_lista()

  @handle("btn_substituir", "click")
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

  @handle("btn_excluir", "click")
  def btn_excluir_click(self, **event_args):
    tag = self.item['tag_instrumento']
    if confirm(f"Tem certeza que deseja remover o instrumento {tag}?"):
      anvil.server.call('remover_instrumento', self.item['row_objeto'])
      Notification(f"Instrumento {tag} removido.", style="success").show()
      self.parent.parent.parent.atualizar_lista()
