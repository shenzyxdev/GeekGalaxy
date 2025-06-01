# desktop_app/ui/sale_list_widget.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
                             QDateEdit, QLineEdit, QFormLayout, QGroupBox, QDialog, QApplication)
from PyQt5.QtCore import Qt, QDate
from api_client.sale_service import get_sales, get_sale_details
from .receipt_dialog import ReceiptDialog
# from .sale_detail_dialog import SaleDetailDialog # Para mostrar detalhes dos itens da venda

class SaleListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relatório de Vendas")

        self.main_layout = QVBoxLayout(self)
        self.init_ui()
        self.load_sales_data() # Carrega os dados ao iniciar o widget

    def init_ui(self):
        # --- Filtros ---
        filter_groupbox = QGroupBox("Filtros de Pesquisa")
        filter_layout = QFormLayout()

        self.data_inicio_input = QDateEdit(self)
        self.data_inicio_input.setCalendarPopup(True)
        self.data_inicio_input.setDate(QDate.currentDate().addMonths(-1)) # Padrão: último mês
        self.data_inicio_input.setDisplayFormat("dd/MM/yyyy")

        self.data_fim_input = QDateEdit(self)
        self.data_fim_input.setCalendarPopup(True)
        self.data_fim_input.setDate(QDate.currentDate()) # Padrão: data atual
        self.data_fim_input.setDisplayFormat("dd/MM/yyyy")

        self.cliente_nome_input = QLineEdit(self)
        self.cliente_nome_input.setPlaceholderText("Nome do cliente...")

        self.vendedor_username_input = QLineEdit(self)
        self.vendedor_username_input.setPlaceholderText("Username do vendedor...")

        self.search_button = QPushButton("Aplicar Filtros e Buscar", self)
        self.search_button.clicked.connect(self.load_sales_data)

        self.clear_filters_button = QPushButton("Limpar Filtros", self)
        self.clear_filters_button.clicked.connect(self.clear_filters_and_load)

        filter_layout.addRow(QLabel("Data Inicial:", self), self.data_inicio_input)
        filter_layout.addRow(QLabel("Data Final:", self), self.data_fim_input)
        filter_layout.addRow(QLabel("Nome do Cliente:", self), self.cliente_nome_input)
        filter_layout.addRow(QLabel("Username Vendedor:", self), self.vendedor_username_input)

        filter_buttons_layout = QHBoxLayout()
        filter_buttons_layout.addWidget(self.search_button)
        filter_buttons_layout.addWidget(self.clear_filters_button)
        filter_layout.addRow(filter_buttons_layout)

        filter_groupbox.setLayout(filter_layout)
        self.main_layout.addWidget(filter_groupbox)

        # --- Tabela de Vendas ---
        title_label = QLabel("Vendas Realizadas")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px; margin-bottom: 5px;")
        self.main_layout.addWidget(title_label)

        self.sales_table = QTableWidget(self)
        # Colunas: ID Venda, Data/Hora, Cliente, Vendedor, Valor Total, Status, Forma Pagamento
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "ID Venda", "Data/Hora", "Cliente", "Vendedor",
            "Valor Total (R$)", "Status Venda", "Forma Pagamento"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setSelectionMode(QTableWidget.SingleSelection)
        # self.sales_table.doubleClicked.connect(self.show_sale_details) # Para ver itens da venda
        self.main_layout.addWidget(self.sales_table)

        # Botão para ver detalhes da venda selecionada (itens)
        self.view_details_button = QPushButton("Ver Detalhes da Venda Selecionada", self)
        self.view_details_button.clicked.connect(self.handle_show_sale_details) # Novo método
        self.view_details_button.setEnabled(False) # Habilita quando uma venda é selecionada

        # Adicionar o botão de detalhes a um novo layout horizontal ou diretamente ao layout principal
        details_button_layout = QHBoxLayout()
        details_button_layout.addStretch() # Empurra o botão para a direita
        details_button_layout.addWidget(self.view_details_button)
        self.main_layout.addLayout(details_button_layout)

        self.sales_table.itemSelectionChanged.connect(
            lambda: self.view_details_button.setEnabled(bool(self.sales_table.selectedItems()))
        )
        self.sales_table.doubleClicked.connect(self.handle_show_sale_details) # Abre detalhes com duplo clique

        self.setLayout(self.main_layout)

    def clear_filters_and_load(self):
        self.data_inicio_input.setDate(QDate.currentDate().addMonths(-1))
        self.data_fim_input.setDate(QDate.currentDate())
        self.cliente_nome_input.clear()
        self.vendedor_username_input.clear()
        self.load_sales_data()

    def load_sales_data(self):
        print("SaleListWidget: Carregando dados das vendas...") # Debug
        self.sales_table.setRowCount(0) # Limpa a tabela

        # Coleta os filtros
        filters = {
            'data_inicio': self.data_inicio_input.date().toString("yyyy-MM-dd"),
            'data_fim': self.data_fim_input.date().toString("yyyy-MM-dd"),
            'cliente_nome': self.cliente_nome_input.text().strip(),
            'vendedor_username': self.vendedor_username_input.text().strip(),
            # Adicionar filtros de statusVenda e formaPagamento se desejar com ComboBoxes
        }
        # Remove filtros vazios para não enviar parâmetros em branco para a API,
        # a menos que a API espere explicitamente por eles.
        active_filters = {k: v for k, v in filters.items() if v}

        success, data_or_error = get_sales(active_filters)

        if success:
            sales_list = data_or_error # get_sales já retorna a lista 'results' se houver paginação
            if isinstance(sales_list, list):
                self.sales_table.setRowCount(len(sales_list))
                for row_num, sale_data in enumerate(sales_list):
                    self.sales_table.setItem(row_num, 0, QTableWidgetItem(str(sale_data.get('id', ''))))

                    data_hora_str = sale_data.get('dataHoraVenda', '')
                    if data_hora_str: # Formatar data/hora
                        try:
                            dt_obj = QDate.fromString(data_hora_str.split("T")[0], Qt.ISODate)
                            # Ou datetime.fromisoformat e depois formatar
                            data_formatada = dt_obj.toString("dd/MM/yyyy") + " " + data_hora_str.split("T")[1].split(".")[0][:5] # HH:mm
                        except:
                            data_formatada = data_hora_str # Fallback
                    else:
                        data_formatada = "N/A"
                    self.sales_table.setItem(row_num, 1, QTableWidgetItem(data_formatada))

                    self.sales_table.setItem(row_num, 2, QTableWidgetItem(str(sale_data.get('cliente_nome', 'N/A'))))
                    self.sales_table.setItem(row_num, 3, QTableWidgetItem(str(sale_data.get('usuario_username', 'N/A'))))
                    self.sales_table.setItem(row_num, 4, QTableWidgetItem(f"R$ {float(sale_data.get('valorTotalVenda', 0.0)):.2f}"))
                    self.sales_table.setItem(row_num, 5, QTableWidgetItem(str(sale_data.get('statusVenda', 'N/A'))))
                    self.sales_table.setItem(row_num, 6, QTableWidgetItem(str(sale_data.get('formaPagamento', 'N/A'))))
                print(f"SaleListWidget: {len(sales_list)} vendas carregadas na tabela.") # Debug
            else:
                QMessageBox.warning(self, "Carregar Vendas", "Resposta da API não é uma lista de vendas.")
                print(f"SaleListWidget: Resposta inesperada da API: {data_or_error}") # Debug
        else:
            error_message = data_or_error.get('detail', "Erro desconhecido ao carregar vendas.")
            QMessageBox.critical(self, "Erro ao Carregar Vendas", error_message)
            print(f"SaleListWidget: Erro ao carregar vendas - {error_message}") # Debug

    def handle_show_sale_details(self):
        selected_rows = self.sales_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Detalhes da Venda", "Nenhuma venda selecionada na tabela.")
            return

        sale_id_item = self.sales_table.item(selected_rows[0].row(), 0) # ID da Venda está na coluna 0
        if not sale_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID da venda selecionada.")
            return

        sale_id_str = sale_id_item.text()
        print(f"SaleListWidget: Mostrando detalhes para venda ID: {sale_id_str}")

        success, sale_details_data = get_sale_details(sale_id_str)

        if success:
            if sale_details_data:
                # O sale_details_data já deve vir da API no formato que ReceiptDialog espera
                # (incluindo 'id', 'dataHoraVenda', 'cliente_nome', 'usuario_username', 'valorTotalVenda', 'formaPagamento', e 'itens')
                # O VendaSerializer com ItemVendaSerializer (many=True, read_only=True) já deve fornecer isso.
                receipt_dialog = ReceiptDialog(sale_data=sale_details_data, parent=self)
                receipt_dialog.exec_()
            else:
                QMessageBox.warning(self, "Detalhes da Venda", "Nenhum detalhe retornado para esta venda.")
        else:
            error_message = sale_details_data.get('detail', "Erro desconhecido ao buscar detalhes da venda.")
            QMessageBox.critical(self, "Erro ao Buscar Detalhes", error_message)

# Bloco para testar o SaleListWidget isoladamente
if __name__ == '__main__':
    import sys
    import os
    # QApplication já está importado no topo do arquivo

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    # Simular um usuário logado com permissão para ver relatórios (ex: Supervisor)
    current_app_state.set_user_info("test_reporter_user", user_id=1, groups=["SUPERVISOR"], is_superuser=True)
    current_app_state.set_auth_tokens("fake_access_for_sale_list_test", "fake_refresh_for_test")

    app = QApplication(sys.argv)
    # Certifique-se que o servidor Django está rodando para get_sales() funcionar
    sale_list_view = SaleListWidget()
    sale_list_view.setGeometry(100, 100, 1000, 600)
    sale_list_view.show()
    sys.exit(app.exec_())