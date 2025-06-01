# desktop_app/ui/select_client_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QDialogButtonBox)
from PyQt5.QtCore import Qt
from api_client.client_service import search_clients # Para buscar clientes
"""from .select_client_dialog import SelectClientDialog"""

class SelectClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Cliente")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        self.selected_client_id = None
        self.selected_client_name = None # Para retornar o nome também

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Layout de Busca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Digite nome, CPF ou e-mail para buscar...")
        self.search_input.returnPressed.connect(self.handle_search) # Busca ao pressionar Enter
        search_button = QPushButton("Buscar Cliente", self)
        search_button.clicked.connect(self.handle_search)
        search_layout.addWidget(QLabel("Buscar:", self))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Tabela de Resultados
        self.results_table = QTableWidget(self)
        self.results_table.setColumnCount(4) # ID, Nome, CPF, E-mail
        self.results_table.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "E-mail"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.doubleClicked.connect(self.handle_select_and_accept) # Seleciona com duplo clique
        main_layout.addWidget(self.results_table)

        # Botões de Ação
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.button(QDialogButtonBox.Ok).setText("Selecionar Cliente")
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False) # Habilita ao selecionar item
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")

        self.button_box.accepted.connect(self.handle_select_and_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.results_table.itemSelectionChanged.connect(self.handle_table_selection_change)
        self.setLayout(main_layout)

    def handle_search(self):
        search_term = self.search_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, "Busca Inválida", "Por favor, digite um termo para a busca.")
            return

        self.results_table.setRowCount(0) # Limpa resultados anteriores
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        print(f"SelectClientDialog: Buscando clientes com termo '{search_term}'")

        success, clients_or_error = search_clients(search_term)
        if success and isinstance(clients_or_error, list):
            if not clients_or_error:
                QMessageBox.information(self, "Busca de Clientes", "Nenhum cliente encontrado.")
                return

            self.results_table.setRowCount(len(clients_or_error))
            for row, client_data in enumerate(clients_or_error):
                self.results_table.setItem(row, 0, QTableWidgetItem(str(client_data.get('id'))))
                self.results_table.setItem(row, 1, QTableWidgetItem(str(client_data.get('nome'))))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(client_data.get('cpf', 'N/A'))))
                self.results_table.setItem(row, 3, QTableWidgetItem(str(client_data.get('email', 'N/A'))))
            print(f"SelectClientDialog: {len(clients_or_error)} clientes carregados.")
        else:
            error_msg = clients_or_error.get('detail', "Erro ao buscar clientes.") if isinstance(clients_or_error, dict) else str(clients_or_error)
            QMessageBox.critical(self, "Erro na Busca", error_msg)
            print(f"SelectClientDialog: Erro ao buscar clientes - {error_msg}")

    def handle_table_selection_change(self):
        selected_items = self.results_table.selectedItems()
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(bool(selected_items))

    def handle_select_and_accept(self):
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Nenhum cliente selecionado na tabela.")
            return

        selected_row_index = selected_rows[0].row()
        client_id_item = self.results_table.item(selected_row_index, 0) # Coluna ID
        client_name_item = self.results_table.item(selected_row_index, 1) # Coluna Nome

        if client_id_item and client_name_item:
            self.selected_client_id = int(client_id_item.text())
            self.selected_client_name = client_name_item.text()
            print(f"SelectClientDialog: Cliente ID {self.selected_client_id} - '{self.selected_client_name}' selecionado.")
            self.accept() # Fecha o diálogo com QDialog.Accepted
        else:
            QMessageBox.critical(self, "Erro de Seleção", "Não foi possível obter os dados do cliente selecionado.")

    def get_selected_client_info(self):
            """Retorna o ID e nome do cliente selecionado, ou (None, None) se nenhum."""
            # self.result() será QDialog.Accepted se o usuário clicou em "Selecionar Cliente" (OK)
            # e o handle_select_and_accept preencheu self.selected_client_id
            if self.result() == QDialog.Accepted and self.selected_client_id is not None:
                return self.selected_client_id, self.selected_client_name
            return None, None

# Bloco de teste isolado
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    current_app_state.set_user_info("test_select_client_user", user_id=1, groups=["ATENDENTE"])
    current_app_state.set_auth_tokens("fake_access_for_select_client_test", "fake_refresh_for_test")

    app = QApplication(sys.argv)
    # Servidor Django precisa estar rodando para search_clients funcionar no teste
    dialog = SelectClientDialog()
    if dialog.exec_() == QDialog.Accepted:
        client_id, client_name = dialog.get_selected_client_info()
        if client_id:
            print(f"TESTE: Cliente Selecionado: ID={client_id}, Nome='{client_name}'")
        else:
            print("TESTE: Nenhum cliente foi efetivamente selecionado apesar do 'Accepted'.")
    else:
        print("TESTE: Diálogo de seleção de cliente cancelado.")
    sys.exit(0)