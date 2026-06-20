from ._anvil_designer import GerenciarInspecoesTemplate
from anvil import *
import anvil.server
from anvil.tables import app_tables

class GerenciarInspecoes(GerenciarInspecoesTemplate):
  def __init__(self, ativo_pai=None, **properties):
    self.init_components(**properties)
    # Guarda a referência do Ativo que foi passado pelo Form principal
    self.ativo_pai = ativo_pai 

    # 1. Carrega unidades para o filtro de Unidade
    unidades = app_tables.unidades.search()
    self.drp_filtro_unidade.items = [("Todas", None)] + [(u['nome_unidade'], u) for u in unidades]

    # 2. Carrega tipos para o filtro de Tipo
    self.drp_filtro_tipo.items = [
      ("Todos", "Todos"), 
      ("Vaso de Pressão", "Vaso de Pressão"), 
      ("Caldeira", "Caldeira"), 
      ("Tanque Metálico", "Tanque Metálico"), 
      ("Tubulação", "Tubulação")
    ]

    # 3. Carrega todos os ativos do banco para o filtro client-side ultra rápido
    self.ativos_completos = list(app_tables.ativos.search())

    # Se foi passado um ativo_pai, define filtros iniciais correspondentes a ele
    if self.ativo_pai:
      self.txt_busca.text = self.ativo_pai['tag']
      self.drp_filtro_tipo.selected_value = self.ativo_pai['tipo']
      if self.ativo_pai['unidade']:
        # Procura correspondente de unidade no dropdown
        for u_text, u_val in self.drp_filtro_unidade.items:
          if u_val and u_val.get_id() == self.ativo_pai['unidade'].get_id():
            self.drp_filtro_unidade.selected_value = u_val
            break

    # Executa a filtragem inicial
    self.filtrar_ativos()

  def filtrar_ativos(self):
    """Filtra a lista de ativos com base no texto de busca, tipo e unidade selecionada"""
    busca = (self.txt_busca.text or "").strip().lower()
    tipo = self.drp_filtro_tipo.selected_value
    unidade = self.drp_filtro_unidade.selected_value

    ativos_filtrados = []
    for a in self.ativos_completos:
      # Filtro de Busca por TAG ou Nome Operacional
      if busca and (busca not in a['tag'].lower() and busca not in (a['nome_operacional'] or "").lower()):
        continue
      # Filtro de Tipo
      if tipo != "Todos" and a['tipo'] != tipo:
        continue
      # Filtro de Unidade
      if unidade is not None:
        if not a['unidade'] or a['unidade'].get_id() != unidade.get_id():
          continue
      
      ativos_filtrados.append(a)

    # Popula o Dropdown final com os ativos filtrados
    self.drp_ativo.items = [(f"{a['tag']} - {a['nome_operacional'] or ''}", a) for a in ativos_filtrados]

    # Decide qual ativo fica selecionado
    if self.ativo_pai and self.ativo_pai in ativos_filtrados:
      self.drp_ativo.selected_value = self.ativo_pai
    else:
      if len(self.drp_ativo.items) > 0:
        self.ativo_pai = self.drp_ativo.items[0][1]
        self.drp_ativo.selected_value = self.ativo_pai
      else:
        self.ativo_pai = None
        self.drp_ativo.selected_value = None

    self.atualizar_lista()

  def txt_busca_change(self, **event_args):
    """Chamado quando digita no campo de busca"""
    self.filtrar_ativos()

  def drp_filtro_tipo_change(self, **event_args):
    """Chamado quando altera o filtro de tipo"""
    self.filtrar_ativos()

  def drp_filtro_unidade_change(self, **event_args):
    """Chamado quando altera o filtro de unidade"""
    self.filtrar_ativos()

  def drp_ativo_change(self, **event_args):
    """Quando o usuário muda o ativo no menu dropdown de ativos filtrados"""
    self.ativo_pai = self.drp_ativo.selected_value
    self.atualizar_lista()

  def atualizar_lista(self):
    """Busca no servidor o histórico de inspeções deste ativo"""
    if not self.ativo_pai:
      self.rp_inspecoes.items = []
      return
    self.rp_inspecoes.items = anvil.server.call('buscar_inspecoes_por_ativo', self.ativo_pai)

  def btn_novo_click(self, **event_args):
    """Abre o formulário para cadastrar uma nova inspeção"""
    if not self.ativo_pai:
      alert("Selecione um ativo antes de cadastrar uma nova inspeção.")
      return

    from GNR13.DialogInspecao import DialogInspecao

    # Instancia o formulário de Inspeção
    form_inspecao = DialogInspecao()

    tag_nome = self.ativo_pai['tag'] if self.ativo_pai else ""

    # Abre o form como um alerta modal
    if alert(content=form_inspecao, title=f"Nova Inspeção: {tag_nome}", buttons=[("Salvar", True), ("Cancelar", False)], large=True):

      # Validação técnica: Relatório e ART são obrigatórios
      if not getattr(form_inspecao.file_relatorio, 'file', None) or not getattr(form_inspecao.file_art, 'file', None):
        alert("Erro: Para conformidade NR-13, o Relatório e a ART são obrigatórios!")
        return

      # Validação da data
      if not form_inspecao.dt_data_inspecao.date:
        alert("Erro: A data da inspeção é obrigatória para calcular o próximo vencimento!")
        return

      dados_relatorio = {
        'data_inspecao': form_inspecao.dt_data_inspecao.date,
        'tipo_inspecao': form_inspecao.drp_tipo_inspecao.selected_value,
        'escopo': form_inspecao.drp_escopo.selected_value,
        'parecer_conclusivo': form_inspecao.chk_apto.checked,
        'num_art': form_inspecao.txt_num_art.text,
        'pdf_relatorio': form_inspecao.file_relatorio.file,
        'pdf_art': form_inspecao.file_art.file
      }

      # Envia ao servidor para calcular a nova data de vencimento
      anvil.server.call('processar_novo_relatorio', self.ativo_pai, dados_relatorio)
      Notification("Inspeção registrada com sucesso!", style="success").show()

      # Atualiza a lista na tela
      self.atualizar_lista()