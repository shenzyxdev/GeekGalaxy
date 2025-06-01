# desktop_app/ui/product_widget.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHBoxLayout, QHeaderView, QDialog)
from PyQt5.QtCore import Qt
from api_client.product_service import get_products, create_product, get_product_by_id, update_product, delete_product  # Importa a função do serviço
from state_manager.app_state import current_app_state # Para verificar permissões
from .add_edit_product_dialog import AddEditProductDialog

class ProductWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciamento de Produtos") # Embora seja um widget, pode ter título se usado em janela separada

        self.main_layout = QVBoxLayout(self)
        self.init_ui()
        self.load_products_data() # Carrega os dados ao iniciar o widget

    def init_ui(self):
        # Título da tela
        title_label = QLabel("Lista de Produtos Cadastrados")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(title_label)

        # Tabela para exibir produtos
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7) # Ajuste conforme os campos que quer mostrar
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Nome", "Categoria", "Valor (R$)",
            "Estoque", "Plataforma", "Cód. Barras"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Colunas esticam
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers) # Não editável diretamente na tabela
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows) # Seleciona a linha inteira
        self.products_table.setSelectionMode(QTableWidget.SingleSelection) # Apenas uma linha por vez
        self.main_layout.addWidget(self.products_table)

        # Layout para Botões de Ação
        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Atualizar Lista")
        self.refresh_button.clicked.connect(self.load_products_data)
        buttons_layout.addWidget(self.refresh_button)

        # Botões de CRUD (visibilidade controlada por permissão)
        # Essas permissões devem ser baseadas nos grupos do usuário
        can_manage_stock = current_app_state.is_user_in_group('ESTOQUISTA') or \
                           current_app_state.is_user_in_group('SUPERVISOR') or \
                           current_app_state.is_current_user_superuser()

        if can_manage_stock:
            self.add_button = QPushButton("Adicionar Novo Produto")
            self.add_button.clicked.connect(self.handle_add_product) # Criaremos este método
            buttons_layout.addWidget(self.add_button)

            self.edit_button = QPushButton("Editar Selecionado")
            self.edit_button.clicked.connect(self.handle_edit_product) # Criaremos este método
            self.edit_button.setEnabled(False) # Habilita quando um item é selecionado
            buttons_layout.addWidget(self.edit_button)

            self.delete_button = QPushButton("Excluir Selecionado")
            self.delete_button.clicked.connect(self.handle_delete_product) # Criaremos este método
            self.delete_button.setEnabled(False) # Habilita quando um item é selecionado
            buttons_layout.addWidget(self.delete_button)

        self.products_table.itemSelectionChanged.connect(self.handle_table_selection_change)

        self.main_layout.addLayout(buttons_layout)
        self.setLayout(self.main_layout)

    def load_products_data(self):
        print("ProductWidget: Carregando dados dos produtos...") # Debug
        self.products_table.setRowCount(0) # Limpa a tabela antes de carregar novos dados
        success, data_or_error = get_products()

        if success:
            if isinstance(data_or_error, list):
                self.products_table.setRowCount(len(data_or_error))
                for row_num, product_data in enumerate(data_or_error):
                    self.products_table.setItem(row_num, 0, QTableWidgetItem(str(product_data.get('id', ''))))
                    self.products_table.setItem(row_num, 1, QTableWidgetItem(str(product_data.get('nomeProduto', 'N/A'))))

                    categoria_info = product_data.get('categoria')
                    cat_nome = categoria_info.get('nomeCategoria', 'N/A') if isinstance(categoria_info, dict) else 'N/A'
                    self.products_table.setItem(row_num, 2, QTableWidgetItem(cat_nome))

                    self.products_table.setItem(row_num, 3, QTableWidgetItem(str(product_data.get('valorUnitario', '0.00'))))
                    self.products_table.setItem(row_num, 4, QTableWidgetItem(str(product_data.get('quantidadeEstoque', '0'))))
                    self.products_table.setItem(row_num, 5, QTableWidgetItem(str(product_data.get('plataforma', 'N/A'))))
                    self.products_table.setItem(row_num, 6, QTableWidgetItem(str(product_data.get('codigoBarras', 'N/A'))))
                print(f"ProductWidget: {len(data_or_error)} produtos carregados na tabela.") # Debug
            else:
                QMessageBox.warning(self, "Carregar Produtos", "Resposta da API não é uma lista de produtos.")
                print(f"ProductWidget: Resposta inesperada da API: {data_or_error}") # Debug

        else:
            error_message = data_or_error.get('detail', "Erro desconhecido ao carregar produtos.")
            QMessageBox.critical(self, "Erro ao Carregar Produtos", error_message)
            print(f"ProductWidget: Erro ao carregar produtos - {error_message}") # Debug

        # Desabilitar botões de edição/exclusão se a tabela estiver vazia ou nada selecionado
        self.handle_table_selection_change()


    def handle_table_selection_change(self):
        selected_items = self.products_table.selectedItems()
        can_manage_stock = hasattr(self, 'edit_button') # Verifica se os botões existem (baseado na permissão)

        if can_manage_stock:
            enable_buttons = bool(selected_items) # Habilita se algo estiver selecionado
            self.edit_button.setEnabled(enable_buttons)
            self.delete_button.setEnabled(enable_buttons)

    def handle_add_product(self):
        print("ProductWidget: Botão Adicionar Novo Produto clicado.") # Debug
        # Cria uma instância do diálogo de adicionar/editar (sem dados, então é para adicionar)
        dialog = AddEditProductDialog(parent=self) # Passa 'self' como pai

        # Executa o diálogo. Se o usuário clicar em "Salvar" e os dados forem válidos no diálogo,
        # dialog.exec_() retornará QDialog.Accepted
        if dialog.exec_() == QDialog.Accepted:
            # Pega os dados do produto do diálogo
            product_data_payload = dialog.get_product_data() # Este método já está no diálogo
            if product_data_payload:
                print(f"ProductWidget: Dados para novo produto: {product_data_payload}") # Debug
                # Chama o serviço para criar o produto na API
                success, response_data_or_error = create_product(product_data_payload)

                if success:
                    created_product_name = response_data_or_error.get('nomeProduto', 'Novo produto')
                    QMessageBox.information(self, "Sucesso",
                                          f"Produto '{created_product_name}' adicionado com sucesso!")
                    self.load_products_data() # Recarrega a lista de produtos para mostrar o novo
                else:
                    error_message = response_data_or_error.get('detail', "Erro desconhecido ao adicionar produto.")
                    QMessageBox.critical(self, "Erro ao Adicionar Produto", error_message)
                    print(f"ProductWidget: Falha ao criar produto - {error_message}") # Debug
        else:
            print("ProductWidget: Diálogo de adicionar produto cancelado.") # Debug

    def handle_edit_product(self):
        selected_rows = self.products_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Editar Produto", "Nenhum produto selecionado para edição.")
            return

        # Pega o ID do produto da primeira coluna da linha selecionada
        product_id_item = self.products_table.item(selected_rows[0].row(), 0)
        if not product_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID do produto selecionado.")
            return
        product_id = product_id_item.text()
        print(f"ProductWidget: Botão Editar clicado para produto ID: {product_id}") # Debug

        # 1. Buscar os detalhes completos do produto pela API para preencher o diálogo
        success_fetch, product_details_or_error = get_product_by_id(product_id)

        if not success_fetch:
            error_message = product_details_or_error.get('detail', f"Erro ao buscar detalhes do produto ID {product_id}.")
            QMessageBox.critical(self, "Erro ao Buscar Produto", error_message)
            return

        # 2. Abrir o diálogo AddEditProductDialog com os dados do produto
        # O product_details_or_error já é o dicionário do produto
        dialog = AddEditProductDialog(product_data=product_details_or_error, parent=self)

        if dialog.exec_() == QDialog.Accepted:
            # 3. Pega os dados (potencialmente modificados) do diálogo
            updated_product_payload = dialog.get_product_data()
            if updated_product_payload:
                print(f"ProductWidget: Dados para atualizar produto ID {product_id}: {updated_product_payload}") # Debug
                # 4. Chama o serviço para atualizar o produto na API
                success_update, response_data_or_error = update_product(product_id, updated_product_payload)

                if success_update:
                    updated_product_name = response_data_or_error.get('nomeProduto', f'Produto ID {product_id}')
                    QMessageBox.information(self, "Sucesso",
                                          f"Produto '{updated_product_name}' atualizado com sucesso!")
                    self.load_products_data() # Recarrega a lista de produtos
                else:
                    error_message = response_data_or_error.get('detail', "Erro desconhecido ao atualizar produto.")
                    QMessageBox.critical(self, "Erro ao Atualizar Produto", error_message)
                    print(f"ProductWidget: Falha ao atualizar produto - {error_message}") # Debug
        else:
            print(f"ProductWidget: Diálogo de editar produto ID {product_id} cancelado.") # Debug
    def handle_delete_product(self):
        selected_rows = self.products_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Excluir Produto", "Nenhum produto selecionado para exclusão.")
            return

        # Pega o ID e o nome do produto da linha selecionada na tabela
        current_row = selected_rows[0].row()
        product_id_item = self.products_table.item(current_row, 0) # Coluna do ID
        product_name_item = self.products_table.item(current_row, 1) # Coluna do Nome

        if not product_id_item or not product_name_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter os dados do produto selecionado.")
            return

        product_id = product_id_item.text()
        product_name = product_name_item.text()
        print(f"ProductWidget: Botão Excluir clicado para produto ID: {product_id}, Nome: {product_name}") # Debug

        # Caixa de diálogo de confirmação
        reply = QMessageBox.question(self, 'Confirmar Exclusão',
                                   f"Tem certeza que deseja excluir o produto:\n'{product_name}' (ID: {product_id})?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print(f"ProductWidget: Usuário confirmou exclusão do produto ID: {product_id}") # Debug
            # Chama o serviço para excluir o produto na API
            success, response_data_or_error = delete_product(product_id)

            if success:
                # A mensagem de sucesso pode vir de response_data_or_error['detail'] se a API retornar algo
                # ou podemos usar uma mensagem padrão se for 204 No Content.
                success_message = response_data_or_error.get('detail', f"Produto '{product_name}' excluído com sucesso!")
                QMessageBox.information(self, "Sucesso", success_message)
                self.load_products_data() # Recarrega a lista de produtos para refletir a exclusão
            else:
                error_message = response_data_or_error.get('detail', "Erro desconhecido ao excluir produto.")
                QMessageBox.critical(self, "Erro ao Excluir Produto", error_message)
                print(f"ProductWidget: Falha ao excluir produto - {error_message}") # Debug
        else:
            print(f"ProductWidget: Usuário cancelou exclusão do produto ID: {product_id}") # Debug

# Bloco para testar o ProductWidget isoladamente
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    # Simular um usuário logado com permissão para gerenciar estoque para teste
    current_app_state.set_user_info("test_estoquista", user_id=1, groups=["ESTOQUISTA"], is_superuser=False)
    current_app_state.set_auth_tokens("fake_access_for_product_widget_test", "fake_refresh_for_test")

    app = QApplication(sys.argv)
    # Certifique-se que o servidor Django está rodando para get_products() funcionar
    product_view = ProductWidget()
    product_view.setGeometry(150, 150, 800, 500) # x, y, largura, altura
    product_view.show()
    sys.exit(app.exec_())