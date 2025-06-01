# desktop_app/ui/add_edit_user_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QDialogButtonBox, QCheckBox,
                             QScrollArea, QWidget, QApplication) # Adicionado QApplication para teste
from PyQt5.QtCore import Qt
from api_client.user_service import get_groups # Para carregar os grupos disponíveis

class AddEditUserDialog(QDialog):
    def __init__(self, user_data=None, existing_usernames=None, parent=None):
        super().__init__(parent)

        self.user_data_to_edit = user_data
        self.is_edit_mode = bool(user_data)
        # Renomeado para all_groups_data para clareza, pois armazena os dicts da API
        self.all_groups_data = []
        self.existing_usernames = existing_usernames if existing_usernames is not None else []
        self.groups_checkboxes = [] # Lista para guardar as QCheckBoxes dos grupos

        self.setWindowTitle("Adicionar Novo Usuário" if not self.is_edit_mode else "Editar Usuário")
        self.setMinimumWidth(450)
        self.setModal(True)

        self.init_ui() # Constroi a UI
        self.load_available_groups() # Carrega os grupos da API para os checkboxes

        # Se estiver editando, preenche os campos com os dados do usuário
        if self.is_edit_mode and self.user_data_to_edit:
            self.populate_fields()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Campos do formulário
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)

        self.is_active_checkbox = QCheckBox("Usuário Ativo", self)
        self.is_active_checkbox.setChecked(True) # Padrão para novo usuário
        self.is_staff_checkbox = QCheckBox("Acesso ao Admin Django (Staff)", self)

        form_layout.addRow(QLabel("Nome de Uuário:"), self.username_input)
        if not self.is_edit_mode: # Senha obrigatória apenas na criação
            form_layout.addRow(QLabel("Senha:"), self.password_input)
            form_layout.addRow(QLabel("Confirmar Senha:"), self.confirm_password_input)
        else: # Em edição, senha é opcional
            self.password_input.setPlaceholderText("Deixe em branco para não alterar")
            self.confirm_password_input.setPlaceholderText("Deixe em branco para não alterar")
            form_layout.addRow(QLabel("Nova Senha (opcional):"), self.password_input)
            form_layout.addRow(QLabel("Confirmar Nova Senha:"), self.confirm_password_input)

        form_layout.addRow(QLabel("Nome:"), self.first_name_input)
        form_layout.addRow(QLabel("Sobrenome:"), self.last_name_input)
        form_layout.addRow(QLabel("E-mail:"), self.email_input)
        form_layout.addRow(self.is_active_checkbox)
        form_layout.addRow(self.is_staff_checkbox)
        main_layout.addLayout(form_layout)

        # --- Seleção de Grupos ---
        groups_label = QLabel("Grupos de Permissão:")
        main_layout.addWidget(groups_label)

        self.groups_scroll_area = QScrollArea(self)
        self.groups_scroll_area.setWidgetResizable(True)
        self.groups_scroll_area.setFixedHeight(100) # Ajuste a altura conforme necessário
        self.groups_widget_container = QWidget() # Widget interno para o scroll
        self.groups_vbox_layout = QVBoxLayout(self.groups_widget_container) # Layout para os checkboxes
        self.groups_scroll_area.setWidget(self.groups_widget_container)
        # self.groups_checkboxes já foi inicializado no __init__
        main_layout.addWidget(self.groups_scroll_area)

        # Botões Salvar e Cancelar
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.button_box.button(QDialogButtonBox.Save).setText("Salvar Usuário")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")

        self.button_box.accepted.connect(self.handle_save)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def load_available_groups(self):
        print("AddEditUserDialog: Carregando grupos disponíveis...")
        # Limpa checkboxes antigos do layout e da lista de referências
        while self.groups_vbox_layout.count():
            child = self.groups_vbox_layout.takeAt(0)
            if child.widget(): # Checa se é um widget (não um espaçador ou layout)
                child.widget().deleteLater()
        self.groups_checkboxes = [] # Limpa a lista de referências de checkboxes
        self.all_groups_data = [] # Limpa os dados de grupos anteriores

        success, groups_api_response = get_groups() # Chama o serviço
        if success and isinstance(groups_api_response, list):
            self.all_groups_data = groups_api_response # Armazena os grupos carregados (lista de dicts)
            if not self.all_groups_data:
                no_groups_label = QLabel("Nenhum grupo de permissão encontrado.", self)
                self.groups_vbox_layout.addWidget(no_groups_label)
                # Não adiciona à self.groups_checkboxes pois não é um checkbox
            else:
                for group_info in self.all_groups_data:
                    group_id = group_info.get('id')
                    group_name = group_info.get('name', f"Grupo ID {group_id if group_id else 'Inválido'}")
                    if group_id is not None: # Apenas adiciona se o ID for válido
                        checkbox = QCheckBox(group_name, self)
                        checkbox.setProperty("group_id", group_id) # Armazena o ID no checkbox
                        self.groups_checkboxes.append(checkbox)   # Adiciona à lista de referências
                        self.groups_vbox_layout.addWidget(checkbox) # Adiciona ao layout
                    else:
                        print(f"DEBUG AddEditUserDialog: Grupo da API sem ID válido: {group_info}")
            print(f"AddEditUserDialog: {len(self.groups_checkboxes)} checkboxes de grupo criados.")
        else:
            error_msg = groups_api_response.get('detail', 'Falha ao carregar grupos.') if isinstance(groups_api_response, dict) else str(groups_api_response)
            error_label = QLabel(f"Erro ao carregar grupos: {error_msg}", self)
            self.groups_vbox_layout.addWidget(error_label)
            QMessageBox.warning(self, "Erro Grupos", error_msg)
            print(f"AddEditUserDialog: Erro ao carregar grupos - {error_msg}")
        
        self.groups_vbox_layout.addStretch() # Para empurrar os checkboxes/mensagens para cima

    def populate_fields(self):
        data = self.user_data_to_edit
        if not data: return

        self.username_input.setText(data.get('username', ''))
        if self.is_edit_mode:
            self.username_input.setReadOnly(True) # Username não editável

        self.first_name_input.setText(data.get('first_name', ''))
        self.last_name_input.setText(data.get('last_name', ''))
        self.email_input.setText(data.get('email', ''))
        self.is_active_checkbox.setChecked(data.get('is_active', True))
        self.is_staff_checkbox.setChecked(data.get('is_staff', False))

        # 'groups' em user_data_to_edit é uma lista de dicts [{'id': x, 'name': 'Y'}]
        user_group_ids = [group.get('id') for group in data.get('groups', []) if group.get('id') is not None]
        
        for checkbox in self.groups_checkboxes:
            group_id_property = checkbox.property("group_id")
            if group_id_property is not None and group_id_property in user_group_ids:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        print(f"AddEditUserDialog: Campos populados para edição. IDs de Grupo do Usuário: {user_group_ids}")

    def get_user_data_payload(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username:
            QMessageBox.warning(self, "Campo Obrigatório", "O nome de usuário não pode estar vazio.")
            return None

        # Verifica duplicidade de username
        current_username_for_check = self.user_data_to_edit.get('username', '').lower() if self.is_edit_mode and self.user_data_to_edit else None
        # Compara com usernames existentes, ignorando o username atual se estiver editando
        other_usernames = [u.lower() for u in self.existing_usernames if u.lower() != current_username_for_check]
        if username.lower() in other_usernames:
            QMessageBox.warning(self, "Erro de Validação", f"O nome de usuário '{username}' já existe.")
            return None

        if not self.is_edit_mode: # Se é novo usuário, senha é obrigatória
            if not password:
                QMessageBox.warning(self, "Campo Obrigatório", "A senha é obrigatória para novos usuários.")
                return None
            if password != confirm_password:
                QMessageBox.warning(self, "Erro de Senha", "As senhas não coincidem.")
                return None
        elif password: # Se está editando E uma nova senha foi digitada
            if password != confirm_password:
                QMessageBox.warning(self, "Erro de Senha", "As senhas não coincidem para a nova senha.")
                return None

        selected_group_ids = []
        for checkbox in self.groups_checkboxes:
            if checkbox.isChecked():
                group_id = checkbox.property("group_id")
                if group_id is not None:
                    try:
                        selected_group_ids.append(int(group_id))
                    except (ValueError, TypeError):
                        print(f"DEBUG AddEditUserDialog: group_id inválido no checkbox e ignorado: {group_id}")
        
        payload = {
            "username": username,
            "email": self.email_input.text().strip() or None,
            "first_name": self.first_name_input.text().strip() or None,
            "last_name": self.last_name_input.text().strip() or None,
            "is_active": self.is_active_checkbox.isChecked(),
            "is_staff": self.is_staff_checkbox.isChecked(),
            "groups_ids": selected_group_ids
        }
        # Adicionar senha apenas se for novo usuário ou se uma nova senha foi explicitamente digitada na edição
        if not self.is_edit_mode or (self.is_edit_mode and password):
            payload['password'] = password
        
        # Não incluir 'id' no payload, pois o UserService.update_user espera o ID como argumento separado
        return payload

    def handle_save(self):
        user_payload = self.get_user_data_payload()
        if user_payload:
            print(f"AddEditUserDialog: Dados coletados para salvar: {user_payload}")
            self.accept()

# Bloco para testar o AddEditUserDialog isoladamente
if __name__ == '__main__':
    import sys
    import os
    # QApplication já importado no topo

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    current_app_state.set_user_info("test_dialog_admin_user", user_id=98, groups=["SUPERVISOR"], is_superuser=True)
    current_app_state.set_auth_tokens("fake_access_for_user_dialog_test", "fake_refresh_for_user_dialog_test")

    app = QApplication(sys.argv)

    print("\n--- Testando diálogo para ADICIONAR usuário (servidor Django precisa estar rodando para carregar grupos) ---")
    add_user_dialog = AddEditUserDialog(existing_usernames=["admin", "supervisor_loja"])
    if add_user_dialog.exec_() == QDialog.Accepted:
        print("ADICIONAR USUÁRIO: Diálogo aceito. Dados:", add_user_dialog.get_user_data_payload())
    else:
        print("ADICIONAR USUÁRIO: Diálogo cancelado.")

    print("\n--- Testando diálogo para EDITAR usuário ---")
    if add_user_dialog.all_groups_data:
        usuario_exemplo_para_editar = {
            "id": 5, "username": "atendente_teste", "email": "atendente@teste.com",
            "first_name": "Ana", "last_name": "Atendente", "is_active": True, "is_staff": False, "is_superuser": False,
            "groups": [g for g in add_user_dialog.all_groups_data if g['name'] == 'ATENDENTE']
        }
        edit_user_dialog = AddEditUserDialog(user_data=usuario_exemplo_para_editar, existing_usernames=["admin", "supervisor_loja"])
        if edit_user_dialog.exec_() == QDialog.Accepted:
            print("EDITAR USUÁRIO: Diálogo aceito. Dados:", edit_user_dialog.get_user_data_payload())
        else:
            print("EDITAR USUÁRIO: Diálogo cancelado.")
    else:
        print("EDITAR USUÁRIO: Teste pulado pois os grupos não foram carregados no diálogo de adição.")

    current_app_state.clear_auth_state()
    sys.exit(0)