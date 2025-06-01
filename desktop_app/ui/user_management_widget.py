# desktop_app/ui/user_management_widget.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDialog, QApplication)
from PyQt5.QtCore import Qt
from .add_edit_user_dialog import AddEditUserDialog # Diálogo para adicionar/editar usuário
from api_client.user_service import get_users, create_user, update_user, get_user_details # Funções do serviço
from state_manager.app_state import current_app_state # Para verificar permissões do usuário logado

class UserManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciamento de Usuários do Sistema")
        self.existing_usernames = [] # Para passar ao diálogo e evitar duplicidade

        self.main_layout = QVBoxLayout(self)
        self.init_ui()
        self.load_users_data() # Carrega os dados ao iniciar o widget

    def init_ui(self):
        title_label = QLabel("Lista de Usuários do Sistema")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(title_label)

        self.users_table = QTableWidget(self)
        # Colunas: ID, Username, Nome Completo, Grupos, Ativo, Staff
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Nome Completo", "Grupos", "Ativo?", "Staff?"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.main_layout.addWidget(self.users_table)

        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar Lista", self)
        self.refresh_button.clicked.connect(self.load_users_data)
        buttons_layout.addWidget(self.refresh_button)

        # Apenas Supervisores (ou superusuários do Django) podem gerenciar usuários
        can_manage_users = current_app_state.is_user_in_group('SUPERVISOR') or \
                           current_app_state.is_current_user_superuser()

        if can_manage_users:
            self.add_button = QPushButton("Adicionar Novo Usuário", self)
            self.add_button.clicked.connect(self.handle_add_user)
            buttons_layout.addWidget(self.add_button)

            self.edit_button = QPushButton("Editar Selecionado", self)
            self.edit_button.clicked.connect(self.handle_edit_user)
            self.edit_button.setEnabled(False)
            buttons_layout.addWidget(self.edit_button)

            # Botão de Ativar/Desativar (ou Excluir) pode ser adicionado aqui depois
            # self.toggle_active_button = QPushButton("Ativar/Desativar", self)
            # self.toggle_active_button.setEnabled(False)
            # buttons_layout.addWidget(self.toggle_active_button)

        self.users_table.itemSelectionChanged.connect(self.handle_table_selection_change)
        self.main_layout.addLayout(buttons_layout)
        self.setLayout(self.main_layout)

    def load_users_data(self):
        print("UserManagementWidget: Carregando dados dos usuários...")
        self.users_table.setRowCount(0)
        self.existing_usernames = [] # Limpa a lista de usernames
        success, data_or_error = get_users()

        if success:
            users_list = data_or_error
            if isinstance(users_list, list):
                self.users_table.setRowCount(len(users_list))
                for row_num, user_data in enumerate(users_list):
                    self.existing_usernames.append(user_data.get('username', '').lower())

                    self.users_table.setItem(row_num, 0, QTableWidgetItem(str(user_data.get('id', ''))))
                    self.users_table.setItem(row_num, 1, QTableWidgetItem(str(user_data.get('username', 'N/A'))))

                    full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                    self.users_table.setItem(row_num, 2, QTableWidgetItem(full_name if full_name else 'N/A'))

                    groups = [g.get('name', '') for g in user_data.get('groups', [])]
                    self.users_table.setItem(row_num, 3, QTableWidgetItem(", ".join(groups) if groups else "Nenhum"))

                    self.users_table.setItem(row_num, 4, QTableWidgetItem("Sim" if user_data.get('is_active') else "Não"))
                    self.users_table.setItem(row_num, 5, QTableWidgetItem("Sim" if user_data.get('is_staff') else "Não"))
                print(f"UserManagementWidget: {len(users_list)} usuários carregados.")
            else:
                QMessageBox.warning(self, "Carregar Usuários", "Resposta da API não é uma lista de usuários.")
        else:
            error_message = data_or_error.get('detail', "Erro desconhecido ao carregar usuários.")
            QMessageBox.critical(self, "Erro ao Carregar Usuários", error_message)
        self.handle_table_selection_change()

    def handle_table_selection_change(self):
        selected_items = self.users_table.selectedItems()
        # Habilita botões de edição/outros se os botões existirem e um item estiver selecionado
        if hasattr(self, 'edit_button'):
            self.edit_button.setEnabled(bool(selected_items))
        # if hasattr(self, 'toggle_active_button'):
        #     self.toggle_active_button.setEnabled(bool(selected_items))

    def handle_add_user(self):
        print("UserManagementWidget: Botão Adicionar Novo Usuário clicado.")
        # Passa a lista de usernames existentes (exceto nenhum, pois é novo usuário)
        dialog = AddEditUserDialog(existing_usernames=self.existing_usernames, parent=self)

        if dialog.exec_() == QDialog.Accepted:
            user_payload = dialog.get_user_data_payload()
            if user_payload:
                print(f"UserManagementWidget: Dados para novo usuário: {user_payload}")
                success, response_data_or_error = create_user(user_payload)
                if success:
                    created_username = response_data_or_error.get('username', 'Novo usuário')
                    QMessageBox.information(self, "Sucesso", f"Usuário '{created_username}' adicionado com sucesso!")
                    self.load_users_data() # Recarrega a lista
                else:
                    error_message = response_data_or_error.get('detail', "Erro ao adicionar usuário.")
                    QMessageBox.critical(self, "Erro ao Adicionar Usuário", error_message)
        else:
            print("UserManagementWidget: Diálogo de adicionar usuário cancelado.")

    def handle_edit_user(self):
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Editar Usuário", "Nenhum usuário selecionado para edição.")
            return

        user_id_item = self.users_table.item(selected_rows[0].row(), 0) # ID está na coluna 0
        if not user_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID do usuário selecionado.")
            return
        user_id = user_id_item.text()
        print(f"UserManagementWidget: Botão Editar clicado para usuário ID: {user_id}")

        success_fetch, user_details_or_error = get_user_details(user_id)
        if not success_fetch:
            error_message = user_details_or_error.get('detail', f"Erro ao buscar detalhes do usuário ID {user_id}.")
            QMessageBox.critical(self, "Erro ao Buscar Usuário", error_message)
            return

        # Passa a lista de usernames existentes, o diálogo saberá ignorar o username atual
        dialog = AddEditUserDialog(user_data=user_details_or_error, existing_usernames=self.existing_usernames, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            updated_user_payload = dialog.get_user_data_payload()
            if updated_user_payload:
                # O ID já está no payload se o get_user_data_payload o incluir no modo de edição
                # Mas a função update_user espera o ID como um argumento separado.
                # Vamos remover o ID do payload se ele estiver lá, pois é parte da URL.
                updated_user_payload.pop('id', None) 
                print(f"UserManagementWidget: Dados para atualizar usuário ID {user_id}: {updated_user_payload}")
                success_update, response_data_or_error = update_user(user_id, updated_user_payload)
                if success_update:
                    updated_username = response_data_or_error.get('username', f'Usuário ID {user_id}')
                    QMessageBox.information(self, "Sucesso", f"Usuário '{updated_username}' atualizado com sucesso!")
                    self.load_users_data()
                else:
                    error_message = response_data_or_error.get('detail', "Erro ao atualizar usuário.")
                    QMessageBox.critical(self, "Erro ao Atualizar Usuário", error_message)
        else:
            print(f"UserManagementWidget: Diálogo de editar usuário ID {user_id} cancelado.")

# Bloco para testar o UserManagementWidget isoladamente
if __name__ == '__main__':
    import sys
    import os
    # QApplication já importado no topo

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    # Simular um usuário Supervisor logado
    current_app_state.set_user_info("test_admin_users", user_id=1, groups=["SUPERVISOR"], is_superuser=True)
    current_app_state.set_auth_tokens("fake_access_for_user_mgmt_test", "fake_refresh_for_user_mgmt_test")

    app = QApplication(sys.argv)
    # Servidor Django precisa estar rodando para get_users() e get_groups() (no diálogo) funcionarem
    user_mgmt_view = UserManagementWidget()
    user_mgmt_view.setGeometry(100, 100, 800, 500)
    user_mgmt_view.show()
    sys.exit(app.exec_())