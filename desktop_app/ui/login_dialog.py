# desktop_app/ui/login_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt

# Importa a função de login do nosso módulo de serviço de autenticação
# Certifique-se de que o caminho para api_client.auth_service está correto
# e que o arquivo config.py é acessível a partir dele.
from api_client.auth_service import login_user, get_current_user_details
from state_manager.app_state import current_app_state

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Login - GeekGalaxy Store")
        self.setMinimumWidth(350)
        self.setModal(True) # Torna o diálogo modal (bloqueia a janela pai até ser fechado)

        # Variáveis para armazenar os tokens e o nome de usuário após o login bem-sucedido
        # Não são mais necessárias aqui, pois usamos o AppState
        # self.access_token = None
        # self.refresh_token = None
        # self.username_logged_in = None # Removido, usamos AppState

        self.init_ui() # Chama o método para construir a interface

    def init_ui(self):
        """Inicializa os componentes da interface do usuário."""
        main_layout = QVBoxLayout(self) # Layout principal vertical para o diálogo

        # Título
        title_label = QLabel("Acesso ao Sistema GeekGalaxy")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Campo Usuário
        self.username_label = QLabel("Usuário:")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Digite seu nome de usuário")
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)

        # Campo Senha
        self.password_label = QLabel("Senha:")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password) # Mascara a senha
        main_layout.addWidget(self.password_label)
        main_layout.addWidget(self.password_input)

        # Espaçador para um melhor visual antes dos botões
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Layout para os Botões (Horizontal)
        buttons_layout = QHBoxLayout()

        # Botão Login
        self.login_button = QPushButton("Login", self)
        self.login_button.setStyleSheet("padding: 8px 15px; font-size: 14px;")
        self.login_button.clicked.connect(self.handle_login_attempt) # Conecta o clique ao método

        # Botão Cancelar
        self.cancel_button = QPushButton("Cancelar", self)
        self.cancel_button.setStyleSheet("padding: 8px 15px; font-size: 14px;")
        self.cancel_button.clicked.connect(self.reject) # self.reject() é um slot padrão de QDialog para fechar e retornar Rejected

        buttons_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def handle_login_attempt(self):
        """Lida com a tentativa de login quando o botão Login é clicado."""
        username_input_text = self.username_input.text().strip()
        password = self.password_input.text()

        if not username_input_text or not password:
            QMessageBox.warning(self, "Erro de Login", "Por favor, preencha o usuário e a senha.")
            return

        print(f"Login Dialog: Tentando login com usuário: '{username_input_text}'")

        login_success, token_data_or_error = login_user(username_input_text, password)

        if login_success:
            access = token_data_or_error.get('access')
            refresh = token_data_or_error.get('refresh')
            current_app_state.set_auth_tokens(access, refresh)

            print(f"Login Dialog: Login inicial bem-sucedido. Buscando detalhes do usuário...")

            user_details_success, user_data_or_error = get_current_user_details(access)

            if user_details_success:
                group_names = [group['name'] for group in user_data_or_error.get('groups', [])]
                current_app_state.set_user_info(
                    username=user_data_or_error.get('username'),
                    user_id=user_data_or_error.get('id'),
                    groups=group_names,
                    is_superuser=user_data_or_error.get('is_superuser', False)
                )

                print(f"Login Dialog: Detalhes do usuário obtidos e AppState atualizado.")
                QMessageBox.information(self, "Login Bem-Sucedido", f"Bem-vindo, {current_app_state.get_username()}!")
                self.accept()
            else:
                error_message = user_data_or_error.get('detail', "Não foi possível buscar os detalhes do usuário após o login.")
                QMessageBox.critical(self, "Falha Pós-Login", error_message)
                current_app_state.clear_auth_state()
                self.password_input.clear()
                self.username_input.setFocus()
        else:
            error_message = token_data_or_error.get('detail', 'Erro desconhecido ao tentar logar.')
            if isinstance(token_data_or_error, str):
                error_message = token_data_or_error

            print(f"Login Dialog: Falha no login inicial - {error_message}")
            QMessageBox.critical(self, "Falha no Login", error_message)
            self.password_input.clear()
            self.username_input.setFocus()

# Bloco para testar o LoginDialog isoladamente
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication # Importação corrigida aqui

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state

    app = QApplication(sys.argv) # sys e QApplication estão definidos
    dialog = LoginDialog()
    result = dialog.exec_()

    if result == QDialog.Accepted:
        print("--- Teste de LoginDialog (Isolado) ---")
        print("Login aceito pela UI!")
        print(f"Usuário Logado (do AppState): {current_app_state.get_username()}")
        print(f"ID do Usuário (do AppState): {current_app_state.get_user_id()}")
        print(f"Grupos do Usuário (do AppState): {current_app_state.get_user_groups()}")
        print(f"É Superuser (do AppState): {current_app_state.is_current_user_superuser()}")
        print(f"Access Token (início, do AppState): {current_app_state.get_access_token()[:20] if current_app_state.get_access_token() else 'N/A'}...")
        print("------------------------------------")
    else:
        print("--- Teste de LoginDialog (Isolado) ---")
        print("Login cancelado ou falhou na UI.")
        print("------------------------------------")
    current_app_state.clear_auth_state()
    sys.exit(0) # sys está definido
