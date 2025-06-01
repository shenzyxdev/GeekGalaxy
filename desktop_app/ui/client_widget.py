# desktop_app/ui/client_widget.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHBoxLayout, QHeaderView, QDialog) # Adicionado QDialog
from PyQt5.QtCore import Qt
from .add_edit_client_dialog import AddEditClientDialog # Diálogo para adicionar/editar
from api_client.client_service import (get_clients, create_client,
                                       get_client_by_id, update_client, delete_client)
from state_manager.app_state import current_app_state

class ClientWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciamento de Clientes")

        self.main_layout = QVBoxLayout(self)
        self.init_ui()
        self.load_clients_data() # Carrega os dados ao iniciar o widget

    def init_ui(self):
        title_label = QLabel("Lista de Clientes Cadastrados")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(title_label)

        self.clients_table = QTableWidget()
        # Definir colunas baseadas nos campos do Cliente que queremos exibir
        self.clients_table.setColumnCount(7)
        self.clients_table.setHorizontalHeaderLabels([
            "ID", "Nome", "CPF", "E-mail", "Telefone", "Cidade", "UF"
        ])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.clients_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.clients_table.setSelectionMode(QTableWidget.SingleSelection)
        self.main_layout.addWidget(self.clients_table)

        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar Lista")
        self.refresh_button.clicked.connect(self.load_clients_data)
        buttons_layout.addWidget(self.refresh_button)

        # Permissões para CRUD de Clientes (Atendente ou Supervisor)
        can_manage_clients = current_app_state.is_user_in_group('ATENDENTE') or \
                             current_app_state.is_user_in_group('SUPERVISOR') or \
                             current_app_state.is_current_user_superuser()

        if can_manage_clients:
            self.add_button = QPushButton("Adicionar Novo Cliente")
            self.add_button.clicked.connect(self.handle_add_client)
            buttons_layout.addWidget(self.add_button)

            self.edit_button = QPushButton("Editar Selecionado")
            self.edit_button.clicked.connect(self.handle_edit_client)
            self.edit_button.setEnabled(False)
            buttons_layout.addWidget(self.edit_button)

            self.delete_button = QPushButton("Excluir Selecionado")
            self.delete_button.clicked.connect(self.handle_delete_client)
            self.delete_button.setEnabled(False)
            buttons_layout.addWidget(self.delete_button)

        self.clients_table.itemSelectionChanged.connect(self.handle_table_selection_change)
        self.main_layout.addLayout(buttons_layout)
        self.setLayout(self.main_layout)

    def load_clients_data(self):
        print("ClientWidget: Carregando dados dos clientes...")
        self.clients_table.setRowCount(0)
        success, data_or_error = get_clients()

        if success:
            if isinstance(data_or_error, list):
                self.clients_table.setRowCount(len(data_or_error))
                for row_num, client_data in enumerate(data_or_error):
                    self.clients_table.setItem(row_num, 0, QTableWidgetItem(str(client_data.get('id', ''))))
                    self.clients_table.setItem(row_num, 1, QTableWidgetItem(str(client_data.get('nome', 'N/A'))))
                    self.clients_table.setItem(row_num, 2, QTableWidgetItem(str(client_data.get('cpf', 'N/A'))))
                    self.clients_table.setItem(row_num, 3, QTableWidgetItem(str(client_data.get('email', 'N/A'))))
                    self.clients_table.setItem(row_num, 4, QTableWidgetItem(str(client_data.get('telefone', 'N/A'))))
                    self.clients_table.setItem(row_num, 5, QTableWidgetItem(str(client_data.get('cidade', 'N/A'))))
                    self.clients_table.setItem(row_num, 6, QTableWidgetItem(str(client_data.get('uf', 'N/A'))))
                print(f"ClientWidget: {len(data_or_error)} clientes carregados na tabela.")
            else:
                QMessageBox.warning(self, "Carregar Clientes", "Resposta da API não é uma lista de clientes.")
                print(f"ClientWidget: Resposta inesperada da API: {data_or_error}")
        else:
            error_message = data_or_error.get('detail', "Erro desconhecido ao carregar clientes.")
            QMessageBox.critical(self, "Erro ao Carregar Clientes", error_message)
            print(f"ClientWidget: Erro ao carregar clientes - {error_message}")
        self.handle_table_selection_change()

    def handle_table_selection_change(self):
        selected_items = self.clients_table.selectedItems()
        can_manage_clients = hasattr(self, 'edit_button') # Verifica se os botões de CRUD existem

        if can_manage_clients:
            enable_buttons = bool(selected_items)
            self.edit_button.setEnabled(enable_buttons)
            self.delete_button.setEnabled(enable_buttons)

    def handle_add_client(self):
        print("ClientWidget: Botão Adicionar Novo Cliente clicado.")
        dialog = AddEditClientDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            client_payload = dialog.get_client_data()
            if client_payload:
                print(f"ClientWidget: Dados para novo cliente: {client_payload}")
                success, response_data_or_error = create_client(client_payload)
                if success:
                    created_client_name = response_data_or_error.get('nome', 'Novo cliente')
                    QMessageBox.information(self, "Sucesso",
                                          f"Cliente '{created_client_name}' adicionado com sucesso!")
                    self.load_clients_data()
                else:
                    error_message = response_data_or_error.get('detail', "Erro desconhecido ao adicionar cliente.")
                    QMessageBox.critical(self, "Erro ao Adicionar Cliente", error_message)
                    print(f"ClientWidget: Falha ao criar cliente - {error_message}")
        else:
            print("ClientWidget: Diálogo de adicionar cliente cancelado.")

    def handle_edit_client(self):
        selected_rows = self.clients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Editar Cliente", "Nenhum cliente selecionado para edição.")
            return

        client_id_item = self.clients_table.item(selected_rows[0].row(), 0)
        if not client_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID do cliente selecionado.")
            return
        client_id = client_id_item.text()
        print(f"ClientWidget: Botão Editar clicado para cliente ID: {client_id}")

        success_fetch, client_details_or_error = get_client_by_id(client_id)
        if not success_fetch:
            error_message = client_details_or_error.get('detail', f"Erro ao buscar detalhes do cliente ID {client_id}.")
            QMessageBox.critical(self, "Erro ao Buscar Cliente", error_message)
            return

        dialog = AddEditClientDialog(client_data=client_details_or_error, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            updated_client_payload = dialog.get_client_data()
            if updated_client_payload:
                print(f"ClientWidget: Dados para atualizar cliente ID {client_id}: {updated_client_payload}")
                success_update, response_data_or_error = update_client(client_id, updated_client_payload)
                if success_update:
                    updated_client_name = response_data_or_error.get('nome', f'Cliente ID {client_id}')
                    QMessageBox.information(self, "Sucesso",
                                          f"Cliente '{updated_client_name}' atualizado com sucesso!")
                    self.load_clients_data()
                else:
                    error_message = response_data_or_error.get('detail', "Erro desconhecido ao atualizar cliente.")
                    QMessageBox.critical(self, "Erro ao Atualizar Cliente", error_message)
                    print(f"ClientWidget: Falha ao atualizar cliente - {error_message}")
        else:
            print(f"ClientWidget: Diálogo de editar cliente ID {client_id} cancelado.")

    def handle_delete_client(self):
        selected_rows = self.clients_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Excluir Cliente", "Nenhum cliente selecionado para exclusão.")
            return

        current_row = selected_rows[0].row()
        client_id_item = self.clients_table.item(current_row, 0)
        client_name_item = self.clients_table.item(current_row, 1)
        if not client_id_item or not client_name_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter os dados do cliente selecionado.")
            return

        client_id = client_id_item.text()
        client_name = client_name_item.text()
        print(f"ClientWidget: Botão Excluir clicado para cliente ID: {client_id}, Nome: {client_name}")

        reply = QMessageBox.question(self, 'Confirmar Exclusão',
                                   f"Tem certeza que deseja excluir o cliente:\n'{client_name}' (ID: {client_id})?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            print(f"ClientWidget: Usuário confirmou exclusão do cliente ID: {client_id}")
            success, response_data_or_error = delete_client(client_id)
            if success:
                success_message = response_data_or_error.get('detail', f"Cliente '{client_name}' excluído com sucesso!")
                QMessageBox.information(self, "Sucesso", success_message)
                self.load_clients_data()
            else:
                error_message = response_data_or_error.get('detail', "Erro desconhecido ao excluir cliente.")
                QMessageBox.critical(self, "Erro ao Excluir Cliente", error_message)
                print(f"ClientWidget: Falha ao excluir cliente - {error_message}")
        else:
            print(f"ClientWidget: Usuário cancelou exclusão do cliente ID: {client_id}")

# Bloco para testar o ClientWidget isoladamente
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    # Simular um usuário logado com permissão para gerenciar clientes
    current_app_state.set_user_info("test_atendente_clients", user_id=1, groups=["ATENDENTE"], is_superuser=False)
    current_app_state.set_auth_tokens("fake_access_for_client_widget_test", "fake_refresh_for_test")

    app = QApplication(sys.argv)
    # Certifique-se que o servidor Django está rodando para get_clients() funcionar
    client_view = ClientWidget()
    client_view.setGeometry(150, 150, 900, 600)
    client_view.show()
    sys.exit(app.exec_())