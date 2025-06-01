# desktop_app/ui/sale_widget.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDoubleSpinBox, QSpinBox, QComboBox, QMessageBox, QFormLayout,
                             QGroupBox, QApplication, QDialog) # Adicionado QApplication para o teste isolado
from PyQt5.QtCore import Qt

# Importações dos serviços e estado
from api_client.product_service import search_products_for_sale
# from api_client.client_service import get_clients, search_clients # Para quando implementar busca de cliente
from api_client.sale_service import create_sale
from state_manager.app_state import current_app_state
from .select_client_dialog import SelectClientDialog
from .receipt_dialog import ReceiptDialog

class SaleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ponto de Venda (PDV)")

        self.current_sale_items = [] # Lista para guardar os dicionários dos itens da venda atual
        self.selected_client_id = None

        self.main_layout = QHBoxLayout(self) # Layout principal horizontal

        self.init_left_panel()  # Painel para adicionar produtos e informações do cliente
        self.init_right_panel() # Painel para itens da venda, total e finalização

        self.setLayout(self.main_layout) # Define o layout principal para este widget
        self.reset_sale_screen() # Prepara a tela para uma nova venda

    def init_left_panel(self):
        left_vbox = QVBoxLayout()

        # --- Grupo de Cliente ---
        client_groupbox = QGroupBox("Cliente (Opcional)")
        client_layout = QFormLayout()
        self.client_search_input = QLineEdit(self)
        self.client_search_input.setPlaceholderText("Buscar por nome ou CPF...")
        self.client_search_button = QPushButton("Buscar/Selecionar Cliente", self)
        self.client_search_button.clicked.connect(self.handle_select_client)
        self.selected_client_label = QLabel("Nenhum cliente selecionado.", self)
        self.clear_client_button = QPushButton("Limpar Cliente", self)
        self.clear_client_button.clicked.connect(self.handle_clear_client)
        self.clear_client_button.setEnabled(False)

        client_layout.addRow(self.client_search_input, self.client_search_button)
        client_layout.addRow(QLabel("Selecionado:", self), self.selected_client_label)
        client_layout.addRow(self.clear_client_button)
        client_groupbox.setLayout(client_layout)
        left_vbox.addWidget(client_groupbox)

        # --- Grupo de Adicionar Produto ---
        product_groupbox = QGroupBox("Adicionar Produto à Venda")
        product_layout = QFormLayout()
        self.product_search_input = QLineEdit(self)
        self.product_search_input.setPlaceholderText("Código de barras ou nome do produto...")
        self.product_search_input.returnPressed.connect(self.handle_add_product_to_sale)

        self.product_quantity_spinbox = QSpinBox(self)
        self.product_quantity_spinbox.setMinimum(1)
        self.product_quantity_spinbox.setValue(1)
        self.product_quantity_spinbox.setMaximum(999)

        self.add_product_button = QPushButton("Adicionar Produto", self)
        self.add_product_button.clicked.connect(self.handle_add_product_to_sale)

        product_layout.addRow(QLabel("Buscar Produto:", self), self.product_search_input)
        product_layout.addRow(QLabel("Quantidade:", self), self.product_quantity_spinbox)
        product_layout.addRow(self.add_product_button)
        product_groupbox.setLayout(product_layout)
        left_vbox.addWidget(product_groupbox)

        left_vbox.addStretch()
        self.main_layout.addLayout(left_vbox, 1)

    def init_right_panel(self):
        right_vbox = QVBoxLayout()

        items_groupbox = QGroupBox("Itens da Venda Atual")
        items_layout = QVBoxLayout()
        self.sale_items_table = QTableWidget(self)
        self.sale_items_table.setColumnCount(5)
        self.sale_items_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço Unit.", "Subtotal", "Remover"])
        self.sale_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sale_items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sale_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.sale_items_table.setColumnWidth(0, 250)
        self.sale_items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        items_layout.addWidget(self.sale_items_table)
        items_groupbox.setLayout(items_layout)
        right_vbox.addWidget(items_groupbox)

        summary_groupbox = QGroupBox("Resumo e Pagamento")
        summary_layout = QFormLayout()
        self.total_sale_label = QLabel("R$ 0.00", self)
        self.total_sale_label.setStyleSheet("font-size: 20px; font-weight: bold; color: blue;")
        self.total_sale_label.setAlignment(Qt.AlignRight)

        self.payment_method_combobox = QComboBox(self)
        self.payment_method_combobox.addItems(["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX"])

        self.finalize_sale_button = QPushButton("Finalizar Venda", self)
        self.finalize_sale_button.setStyleSheet("padding: 10px; font-size: 16px; background-color: green; color: white;")
        self.finalize_sale_button.clicked.connect(self.handle_finalize_sale)
        self.finalize_sale_button.setEnabled(False)

        summary_layout.addRow(QLabel("TOTAL DA VENDA:", self), self.total_sale_label)
        summary_layout.addRow(QLabel("Forma de Pagamento:", self), self.payment_method_combobox)
        summary_layout.addRow(self.finalize_sale_button)
        summary_groupbox.setLayout(summary_layout)
        right_vbox.addWidget(summary_groupbox)

        self.main_layout.addLayout(right_vbox, 2)

    def update_sale_summary(self):
        self.sale_items_table.setRowCount(0)
        current_total = 0.0

        if not self.current_sale_items:
            self.total_sale_label.setText("R$ 0.00")
            self.finalize_sale_button.setEnabled(False)
            return

        self.sale_items_table.setRowCount(len(self.current_sale_items))
        for row, item_data in enumerate(self.current_sale_items):
            self.sale_items_table.setItem(row, 0, QTableWidgetItem(item_data['product_name']))
            self.sale_items_table.setItem(row, 1, QTableWidgetItem(str(item_data['quantity'])))
            self.sale_items_table.setItem(row, 2, QTableWidgetItem(f"R$ {item_data['unit_price']:.2f}"))
            subtotal = item_data['quantity'] * item_data['unit_price']
            self.sale_items_table.setItem(row, 3, QTableWidgetItem(f"R$ {subtotal:.2f}"))
            current_total += subtotal

            remove_button = QPushButton("X", self)
            remove_button.setStyleSheet("color: red; font-weight: bold;")
            remove_button.setToolTip(f"Remover {item_data['product_name']} da venda")
            remove_button.clicked.connect(lambda checked, pid=item_data['product_id']: self.handle_remove_item_from_sale(pid))
            self.sale_items_table.setCellWidget(row, 4, remove_button)

        self.total_sale_label.setText(f"R$ {current_total:.2f}")
        self.finalize_sale_button.setEnabled(True)

    def reset_sale_screen(self):
        self.selected_client_id = None
        self.selected_client_label.setText("Nenhum cliente selecionado.")
        self.clear_client_button.setEnabled(False)
        self.client_search_input.clear()
        self.product_search_input.clear()
        self.product_quantity_spinbox.setValue(1)
        self.current_sale_items = []
        self.update_sale_summary()
        self.payment_method_combobox.setCurrentIndex(0)
        self.product_search_input.setFocus()
        print("SaleWidget: Tela de venda resetada.")

    def handle_select_client(self):
        print("SaleWidget: Botão Buscar/Selecionar Cliente clicado.")
        # Cria uma instância do diálogo de seleção de cliente
        # Passa 'self' como pai para que o diálogo seja modal em relação ao SaleWidget
        select_dialog = SelectClientDialog(self)

        # Executa o diálogo. O código pausa aqui até que o diálogo seja fechado.
        # dialog_result será QDialog.Accepted se o usuário clicar em "Selecionar Cliente" (OK)
        # e o handle_select_and_accept do diálogo tiver chamado self.accept()
        dialog_result = select_dialog.exec_()

        if dialog_result == QDialog.Accepted:
            # Pega as informações do cliente selecionado do diálogo
            client_id, client_name = select_dialog.get_selected_client_info()

            if client_id and client_name:
                self.selected_client_id = client_id
                self.selected_client_label.setText(f"{client_name} (ID: {client_id})")
                self.clear_client_button.setEnabled(True) # Habilita o botão de limpar
                print(f"SaleWidget: Cliente ID {client_id} - '{client_name}' selecionado para a venda.")
            else:
                # Isso pode acontecer se o diálogo foi aceito mas, por algum motivo,
                # get_selected_client_info não retornou dados válidos (improvável com a lógica atual do diálogo)
                self.handle_clear_client() # Garante que o estado seja limpo
                print("SaleWidget: Diálogo de cliente aceito, mas nenhuma informação de cliente válida foi retornada.")
        else:
            # Usuário fechou o diálogo clicando em "Cancelar" ou no "X"
            print("SaleWidget: Diálogo de seleção de cliente cancelado ou fechado.")

    def handle_clear_client(self):
        self.selected_client_id = None
        self.selected_client_label.setText("Nenhum cliente selecionado.")
        self.clear_client_button.setEnabled(False)
        self.client_search_input.clear() # Limpa também o campo de busca de cliente
        print("SaleWidget: Seleção de cliente limpa.")

    def handle_add_product_to_sale(self):
        search_term = self.product_search_input.text().strip()
        quantity_to_add = self.product_quantity_spinbox.value()

        if not search_term:
            QMessageBox.warning(self, "Adicionar Produto", "Digite o nome ou código do produto para buscar.")
            self.product_search_input.setFocus()
            return
        if quantity_to_add <= 0:
            QMessageBox.warning(self, "Adicionar Produto", "A quantidade deve ser pelo menos 1.")
            self.product_quantity_spinbox.setFocus()
            return
        
        print(f"SaleWidget: Buscando produto '{search_term}' para adicionar {quantity_to_add} unidade(s).")
        success, products_or_error = search_products_for_sale(search_term)

        if not success:
            error_message = products_or_error.get('detail', "Erro ao buscar produto.")
            QMessageBox.critical(self, "Erro na Busca", error_message)
            return

        found_products = products_or_error
        selected_product_data = None

        if not found_products:
            QMessageBox.information(self, "Busca de Produto", f"Nenhum produto encontrado para '{search_term}'.")
            return
        elif len(found_products) == 1:
            selected_product_data = found_products[0]
            print(f"SaleWidget: Produto único encontrado: {selected_product_data.get('nomeProduto')}")
        else:
            QMessageBox.information(self, "Múltiplos Produtos",
                                  f"{len(found_products)} produtos encontrados para '{search_term}'.\n"
                                  "Selecionando o primeiro da lista para este exemplo.\n"
                                  "(Funcionalidade de seleção múltipla a ser implementada).")
            selected_product_data = found_products[0]

        if not selected_product_data:
            return

        product_id = selected_product_data.get('id')
        product_name = selected_product_data.get('nomeProduto', 'Produto Desconhecido')
        unit_price = float(selected_product_data.get('valorUnitario', 0.0))
        stock_available = int(selected_product_data.get('quantidadeEstoque', 0))

        if quantity_to_add > stock_available:
            QMessageBox.warning(self, "Estoque Insuficiente",
                              f"Estoque insuficiente para '{product_name}'.\n"
                              f"Disponível: {stock_available}, Solicitado: {quantity_to_add}.")
            return

        existing_item_index = -1
        for i, item in enumerate(self.current_sale_items):
            if item['product_id'] == product_id:
                existing_item_index = i
                break
        
        if existing_item_index != -1:
            new_quantity = self.current_sale_items[existing_item_index]['quantity'] + quantity_to_add
            if new_quantity > stock_available:
                 QMessageBox.warning(self, "Estoque Insuficiente",
                              f"Não é possível adicionar mais '{product_name}'.\n"
                              f"Total em estoque: {stock_available}. Já na venda: {self.current_sale_items[existing_item_index]['quantity']}. Solicitado agora: {quantity_to_add}.")
                 return
            self.current_sale_items[existing_item_index]['quantity'] = new_quantity
            print(f"SaleWidget: Quantidade do produto '{product_name}' atualizada para {new_quantity}.")
        else:
            sale_item_data = {
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity_to_add,
                'unit_price': unit_price,
                'stock_available': stock_available
            }
            self.current_sale_items.append(sale_item_data)
            print(f"SaleWidget: Produto '{product_name}' adicionado à venda.")

        self.update_sale_summary()
        self.product_search_input.clear()
        self.product_quantity_spinbox.setValue(1)
        self.product_search_input.setFocus()

    def handle_remove_item_from_sale(self, product_id_to_remove):
        print(f"SaleWidget: Tentando remover item com product_id: {product_id_to_remove}")
        # Recria a lista excluindo o item com o product_id correspondente
        # Se houver múltiplos itens com o mesmo product_id (não deveria com a lógica atual de incrementar),
        # esta abordagem removeria todos. Para remover apenas uma instância, seria necessário um ID de item de venda único.
        self.current_sale_items = [item for item in self.current_sale_items if item['product_id'] != product_id_to_remove]
        self.update_sale_summary()
        # Não precisa de QMessageBox aqui, a remoção visual da tabela é o feedback.
        # QMessageBox.information(self, "Item Removido", f"Item (ID {product_id_to_remove}) removido da venda.")

    def handle_finalize_sale(self): # MÉTODO CORRIGIDO PARA ESTAR DENTRO DA CLASSE
        if not self.current_sale_items:
            QMessageBox.warning(self, "Finalizar Venda", "Não há itens na venda para finalizar.")
            return

        payment_method_text = self.payment_method_combobox.currentText()
        payment_method_api_value = ""
        if payment_method_text == "Dinheiro":
            payment_method_api_value = "DINHEIRO"
        elif payment_method_text == "Cartão de Crédito":
            payment_method_api_value = "CARTAO_CREDITO"
        elif payment_method_text == "Cartão de Débito":
            payment_method_api_value = "CARTAO_DEBITO"
        elif payment_method_text == "PIX":
            payment_method_api_value = "PIX"
        else:
            QMessageBox.warning(self, "Forma de Pagamento", "Forma de pagamento inválida selecionada.")
            return

        items_payload = []
        for item in self.current_sale_items:
            items_payload.append({
                "produto_id": item['product_id'],
                "quantidade": item['quantity'],
                "precoUnitarioVenda": str(item['unit_price'])
            })

        sale_data_payload = {
            "cliente_id": self.selected_client_id,
            "formaPagamento": payment_method_api_value,
            "statusPagamento": "PAGO",
            "statusVenda": "CONCLUIDA",
            "itens": items_payload
        }

        print(f"SaleWidget: Tentando finalizar venda com payload: {sale_data_payload}")
        total_venda_str = self.total_sale_label.text()
        reply = QMessageBox.question(self, 'Confirmar Venda',
                                   f"Total da Venda: {total_venda_str}\n"
                                   f"Forma de Pagamento: {payment_method_text}\n\n"
                                   "Deseja finalizar esta venda?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            print("SaleWidget: Finalização da venda cancelada pelo usuário.")
            return

        success, response_data_or_error = create_sale(sale_data_payload)

        if success:
            # A API retorna a venda criada, incluindo seu ID, valorTotalVenda calculado,
            # e os itens com seus detalhes (incluindo o objeto produto aninhado se o serializer estiver assim).
            created_sale_data = response_data_or_error # Esta é a venda completa retornada pela API

            sale_id = created_sale_data.get('id')
            total_calculado_api = created_sale_data.get('valorTotalVenda', 'N/A')

            QMessageBox.information(self, "Venda Finalizada",
                                  f"Venda #{sale_id} registrada com sucesso!\n"
                                  f"Total: R$ {total_calculado_api}")

            # Mostrar o diálogo de recibo
            # Precisamos garantir que 'created_sale_data' tenha o formato que ReceiptDialog espera
            # VendaSerializer retorna 'itens' com ItemVendaSerializer (que tem 'produto' nested)
            # e 'cliente_nome', 'usuario_username'.
            receipt_dialog = ReceiptDialog(sale_data=created_sale_data, parent=self)
            receipt_dialog.exec_() # Mostra o diálogo de recibo

            self.reset_sale_screen() # Limpa a tela para uma nova venda
        else:
            error_message = response_data_or_error.get('detail', "Erro desconhecido ao finalizar a venda.")
            QMessageBox.critical(self, "Erro ao Finalizar Venda", error_message)
            print(f"SaleWidget: Falha ao finalizar venda - {error_message}")

# Bloco para testar o SaleWidget isoladamente
if __name__ == '__main__':
    import sys
    import os
    # QApplication já está importado no topo do arquivo

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    current_app_state.set_user_info("test_pdv_user", user_id=1, groups=["ATENDENTE"])
    current_app_state.set_auth_tokens("fake_access_for_sale_widget_test", "fake_refresh_for_test")

    app = QApplication(sys.argv)
    sale_view = SaleWidget()
    sale_view.setGeometry(100, 100, 1000, 600)
    sale_view.show()
    sys.exit(app.exec_())