# desktop_app/ui/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QMessageBox, QStackedWidget, QAction, QStatusBar, QMenu, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

# Importa os widgets das telas que usaremos
from .product_widget import ProductWidget
from .client_widget import ClientWidget
from .sale_widget import SaleWidget
from .sale_list_widget import SaleListWidget
from .user_management_widget import UserManagementWidget # Importa o UserManagementWidget

# Importa o estado global da aplicação
from state_manager.app_state import current_app_state

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.username = current_app_state.get_username()
        self.user_groups = current_app_state.get_user_groups()
        self.is_superuser = current_app_state.is_current_user_superuser()

        self.setWindowTitle(f"GeekGalaxy Store - Usuário: {self.username}")
        self.setGeometry(100, 100, 900, 700)

        self.init_ui_and_widgets()
        self.create_menus()
        self.create_status_bar()
        self.show_initial_screen()

    def init_ui_and_widgets(self):
        """Inicializa a UI base e os principais widgets de tela."""
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        self.welcome_screen = QLabel(f"Bem-vindo ao Sistema GeekGalaxy, {self.username}!\nSelecione uma opção no menu.")
        self.welcome_screen.setAlignment(Qt.AlignCenter)
        self.welcome_screen.setStyleSheet("font-size: 20px;")
        self.stacked_widget.addWidget(self.welcome_screen)

        self.product_widget_instance = ProductWidget(self)
        self.stacked_widget.addWidget(self.product_widget_instance)

        self.client_widget_instance = ClientWidget(self)
        self.stacked_widget.addWidget(self.client_widget_instance)

        self.sale_widget_instance = SaleWidget(self)
        self.stacked_widget.addWidget(self.sale_widget_instance)

        self.sale_list_widget_instance = SaleListWidget(self)
        self.stacked_widget.addWidget(self.sale_list_widget_instance)
        
        # Instanciar e adicionar o UserManagementWidget
        self.user_management_widget_instance = UserManagementWidget(self) # ADICIONADO
        self.stacked_widget.addWidget(self.user_management_widget_instance) # ADICIONADO

    def create_menus(self):
        menubar = self.menuBar()
        can_supervise = 'SUPERVISOR' in self.user_groups or self.is_superuser
        can_attend = 'ATENDENTE' in self.user_groups or can_supervise
        can_stock = 'ESTOQUISTA' in self.user_groups or can_supervise

        print(f"DEBUG MainWindow create_menus: User: {self.username}, Groups: {self.user_groups}, IsSuperuser: {self.is_superuser}")
        print(f"DEBUG MainWindow create_menus: can_supervise: {can_supervise}, can_attend: {can_attend}, can_stock: {can_stock}")

        file_menu = menubar.addMenu('&Arquivo')
        logout_action = QAction('&Logout', self)
        logout_action.setStatusTip('Sair do sistema e voltar para a tela de login')
        logout_action.triggered.connect(self.handle_logout)
        file_menu.addAction(logout_action)

        exit_action = QAction('&Sair da Aplicação', self)
        exit_action.setStatusTip('Fechar o programa')
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close_application)
        file_menu.addAction(exit_action)

        if can_stock or can_attend:
            cadastros_menu = menubar.addMenu('&Cadastros')
            if can_stock:
                produtos_action = QAction('&Produtos', self)
                produtos_action.setStatusTip('Gerenciar cadastro de produtos')
                produtos_action.triggered.connect(self.show_product_screen)
                cadastros_menu.addAction(produtos_action)
            if can_attend:
                clientes_action = QAction('&Clientes', self)
                clientes_action.setStatusTip('Gerenciar cadastro de clientes')
                clientes_action.triggered.connect(self.show_client_screen)
                cadastros_menu.addAction(clientes_action)
        
        if can_attend:
            vendas_menu = menubar.addMenu('&Vendas')
            realizar_venda_action = QAction('&Realizar Venda (PDV)', self)
            realizar_venda_action.setStatusTip('Abrir o Ponto de Venda')
            realizar_venda_action.triggered.connect(self.show_sale_screen)
            vendas_menu.addAction(realizar_venda_action)

        if can_supervise:
            admin_menu = menubar.addMenu('&Administração')
            
            sales_report_action = QAction('&Relatório de Vendas', self)
            sales_report_action.setStatusTip('Consultar e filtrar vendas realizadas')
            sales_report_action.triggered.connect(self.show_sales_report_screen)
            admin_menu.addAction(sales_report_action)

            usuarios_action = QAction('&Gerenciar Usuários', self)
            usuarios_action.setStatusTip('Gerenciar usuários do sistema desktop') # Modificado o StatusTip
            usuarios_action.triggered.connect(self.show_user_management_screen) # Conectado corretamente
            admin_menu.addAction(usuarios_action)

    def create_status_bar(self):
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.update_status_bar()

    def update_status_bar(self):
        user_groups_str = ", ".join(self.user_groups) if self.user_groups else "Nenhum"
        is_su_str = " (Django Superuser)" if self.is_superuser else ""
        self.statusBar.showMessage(f"Usuário: {self.username}{is_su_str} | Grupos: [{user_groups_str}] | Pronto")

    def show_initial_screen(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.update_status_bar()
        self.setWindowTitle(f"GeekGalaxy Store - Usuário: {self.username}")

    def show_product_screen(self):
        print("MainWindow: Mostrando tela de produtos.")
        self.stacked_widget.setCurrentWidget(self.product_widget_instance)
        self.product_widget_instance.load_products_data()
        self.statusBar.showMessage("Acessada: Tela de Gerenciamento de Produtos")

    def show_client_screen(self):
        print("MainWindow: Mostrando tela de clientes.")
        self.stacked_widget.setCurrentWidget(self.client_widget_instance)
        self.client_widget_instance.load_clients_data()
        self.statusBar.showMessage("Acessada: Tela de Gerenciamento de Clientes")

    def show_sale_screen(self):
        print("MainWindow: Mostrando tela de Ponto de Venda (PDV).")
        self.stacked_widget.setCurrentWidget(self.sale_widget_instance)
        self.sale_widget_instance.reset_sale_screen()
        self.statusBar.showMessage("Acessada: Tela de Vendas (PDV)")

    def show_sales_report_screen(self):
        print("MainWindow: Mostrando tela de Relatório de Vendas.")
        self.stacked_widget.setCurrentWidget(self.sale_list_widget_instance)
        self.sale_list_widget_instance.load_sales_data()
        self.statusBar.showMessage("Acessada: Tela de Relatório de Vendas")

    # MÉTODO ATUALIZADO para o UserManagementWidget
    def show_user_management_screen(self):
        print("MainWindow: Mostrando tela de Gerenciamento de Usuários.")
        self.stacked_widget.setCurrentWidget(self.user_management_widget_instance)
        self.user_management_widget_instance.load_users_data() # Chama o método para carregar os dados
        self.statusBar.showMessage("Acessada: Tela de Gerenciamento de Usuários")

    def handle_logout(self):
        print("DEBUG MainWindow: handle_logout chamado")
        reply = QMessageBox.question(self, 'Logout', "Tem certeza que deseja sair?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            print("DEBUG MainWindow: Usuário confirmou logout")
            current_app_state.clear_auth_state()
            self.close()
        else:
            print("DEBUG MainWindow: Usuário cancelou logout")

    def close_application(self):
        print("DEBUG MainWindow: close_application chamado")
        reply = QMessageBox.question(self, 'Sair da Aplicação', "Tem certeza que deseja fechar o programa?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            print("DEBUG MainWindow: Usuário confirmou sair da aplicação")
            QApplication.instance().quit()
        else:
            print("DEBUG MainWindow: Usuário cancelou sair da aplicação")

    def closeEvent(self, event):
        print("DEBUG MainWindow: closeEvent (fechamento pelo 'X') chamado")
        super().closeEvent(event)

# Bloco para testar a MainWindow isoladamente
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state

    print("TESTE ISOLADO MainWindow: Configurando como SUPERVISOR (grupo)")
    current_app_state.set_user_info("test_supervisor_usermgmt", user_id=2, groups=["SUPERVISOR"], is_superuser=False)
    current_app_state.set_auth_tokens("fake_access_for_main_window_test", "fake_refresh_for_test")

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    exit_code = app.exec_()
    current_app_state.clear_auth_state()
    sys.exit(exit_code)