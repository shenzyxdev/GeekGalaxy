# desktop_app/main.py
import sys  # <--- IMPORTAR SYS AQUI
import os
from PyQt5.QtWidgets import QApplication, QDialog # <--- IMPORTAR QApplication e QDialog AQUI

# Adiciona o diretório 'desktop_app' ao sys.path para encontrar sub-módulos
# Isso é crucial para que os imports como 'from ui.login_dialog import ...' funcionem
# Esta linha garante que o diretório onde este script (main.py) está seja adicionado ao path.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from state_manager.app_state import current_app_state # Importa a instância do AppState

def run_app():
    app = QApplication(sys.argv) # Agora QApplication e sys estão definidos

    while True: # Loop para permitir relogin após logout
        # current_app_state.clear_auth_state() # O logout na MainWindow já faz isso

        login_dialog = LoginDialog()
        login_result = login_dialog.exec_() # .exec_() torna o diálogo modal e espera

        # QDialog.Accepted é uma constante de QDialog, que importamos
        if login_result == QDialog.Accepted and current_app_state.is_authenticated():
            print("Main.py: Login aceito, mostrando MainWindow.")
            main_window = MainWindow()
            main_window.show()
            app.exec_() # Este exec_() inicia o loop de eventos para a MainWindow

            # Quando main_window.close() é chamado (ex: no logout ou no "X")
            # app.exec_() termina e o código continua aqui.
            if not current_app_state.is_authenticated(): # Usuário fez logout
                print("Main.py: Usuário fez logout, voltando para tela de login.")
                # O loop 'while True' reiniciará e mostrará o LoginDialog
                continue
            else: # Janela principal fechada sem logout (ex: clicou no 'X')
                print("Main.py: Janela principal fechada pelo 'X'. Encerrando aplicação.")
                break # Sai do loop while e encerra a aplicação
        else:
            # Login cancelado ou falhou, sair da aplicação
            print("Main.py: Login cancelado ou falhou. Encerrando aplicação.")
            break # Sai do loop while e encerra a aplicação
    sys.exit(0) # Garante que a aplicação saia limpa (agora sys está definido)

if __name__ == '__main__':
    run_app()