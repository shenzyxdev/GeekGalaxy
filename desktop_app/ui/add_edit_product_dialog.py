# desktop_app/ui/add_edit_product_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                             QTextEdit, QDoubleSpinBox, QSpinBox, QComboBox,
                             QPushButton, QMessageBox, QHBoxLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt
from api_client.category_service import get_categories # Para carregar categorias

class AddEditProductDialog(QDialog):
    def __init__(self, product_data=None, parent=None):
        """
        Construtor do diálogo.
        product_data: Dicionário com dados de um produto para edição, ou None para adição.
        """
        super().__init__(parent)

        self.product_data_to_edit = product_data # Armazena dados para edição
        self.is_edit_mode = bool(product_data)

        self.setWindowTitle("Adicionar Novo Produto" if not self.is_edit_mode else "Editar Produto")
        self.setMinimumWidth(450)
        self.setModal(True)

        self.init_ui()
        self.load_categories()

        if self.is_edit_mode:
            self.populate_fields()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout() # Layout de formulário para labels e campos

        # Campos do formulário
        self.nome_produto_input = QLineEdit(self)
        self.codigo_barras_input = QLineEdit(self)
        self.descricao_input = QTextEdit(self) # Para textos mais longos
        self.descricao_input.setFixedHeight(80) # Ajusta altura
        self.categoria_combobox = QComboBox(self)
        self.valor_unitario_spinbox = QDoubleSpinBox(self)
        self.valor_unitario_spinbox.setDecimals(2)
        self.valor_unitario_spinbox.setMinimum(0.00)
        self.valor_unitario_spinbox.setMaximum(99999.99)
        self.valor_unitario_spinbox.setPrefix("R$ ")
        self.quantidade_estoque_spinbox = QSpinBox(self)
        self.quantidade_estoque_spinbox.setMinimum(0)
        self.quantidade_estoque_spinbox.setMaximum(99999)
        self.plataforma_input = QLineEdit(self) # Para jogos/acessórios
        self.garantia_input = QLineEdit(self)   # Para jogos/acessórios

        form_layout.addRow(QLabel("Nome do Produto:"), self.nome_produto_input)
        form_layout.addRow(QLabel("Código de Barras:"), self.codigo_barras_input)
        form_layout.addRow(QLabel("Descrição:"), self.descricao_input)
        form_layout.addRow(QLabel("Categoria:"), self.categoria_combobox)
        form_layout.addRow(QLabel("Valor Unitário:"), self.valor_unitario_spinbox)
        form_layout.addRow(QLabel("Qtde. em Estoque:"), self.quantidade_estoque_spinbox)
        form_layout.addRow(QLabel("Plataforma (Jogos/Acessórios):"), self.plataforma_input)
        form_layout.addRow(QLabel("Prazo de Garantia:"), self.garantia_input)

        main_layout.addLayout(form_layout)

        # Botões Salvar e Cancelar
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.button_box.button(QDialogButtonBox.Save).setText("Salvar")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")

        self.button_box.accepted.connect(self.handle_save) # Conecta o sinal 'accepted' (botão Salvar)
        self.button_box.rejected.connect(self.reject)    # Conecta o sinal 'rejected' (botão Cancelar)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def load_categories(self):
        print("AddEditProductDialog: Carregando categorias...") # Debug
        self.categoria_combobox.clear()
        self.categoria_combobox.addItem("Carregando categorias...", None) # Item temporário
        self.categoria_combobox.setEnabled(False)

        success, categories_or_error = get_categories()
        if success and isinstance(categories_or_error, list):
            self.categoria_combobox.clear() # Limpa o item "Carregando..."
            if not categories_or_error:
                self.categoria_combobox.addItem("Nenhuma categoria encontrada", None)
            else:
                self.categoria_combobox.addItem("Selecione uma categoria...", None) # Placeholder
                for cat in categories_or_error:
                    # Armazena o ID da categoria como 'userData' no item do ComboBox
                    self.categoria_combobox.addItem(cat.get('nomeCategoria', 'N/A'), cat.get('id'))
            self.categoria_combobox.setEnabled(True)
            print(f"AddEditProductDialog: {len(categories_or_error)} categorias carregadas.") # Debug
        else:
            self.categoria_combobox.clear()
            self.categoria_combobox.addItem("Erro ao carregar categorias", None)
            error_msg = categories_or_error.get('detail', 'Falha ao carregar categorias.') if isinstance(categories_or_error, dict) else str(categories_or_error)
            QMessageBox.warning(self, "Categorias", error_msg)
            print(f"AddEditProductDialog: Erro ao carregar categorias - {error_msg}") # Debug

    def populate_fields(self):
        """Preenche os campos se estiver no modo de edição."""
        if not self.product_data_to_edit:
            return

        self.nome_produto_input.setText(self.product_data_to_edit.get('nomeProduto', ''))
        self.codigo_barras_input.setText(self.product_data_to_edit.get('codigoBarras', ''))
        self.descricao_input.setPlainText(self.product_data_to_edit.get('descricao', ''))
        self.valor_unitario_spinbox.setValue(float(self.product_data_to_edit.get('valorUnitario', 0.0)))
        self.quantidade_estoque_spinbox.setValue(int(self.product_data_to_edit.get('quantidadeEstoque', 0)))
        self.plataforma_input.setText(self.product_data_to_edit.get('plataforma', ''))
        self.garantia_input.setText(self.product_data_to_edit.get('prazoGarantia', ''))

        # Selecionar a categoria correta no ComboBox
        categoria_data = self.product_data_to_edit.get('categoria') # No serializer, 'categoria' é o objeto serializado
        if categoria_data and isinstance(categoria_data, dict):
            categoria_id_to_select = categoria_data.get('id')
            if categoria_id_to_select is not None:
                for index in range(self.categoria_combobox.count()):
                    if self.categoria_combobox.itemData(index) == categoria_id_to_select:
                        self.categoria_combobox.setCurrentIndex(index)
                        break
        print("AddEditProductDialog: Campos populados para edição.") # Debug


    def get_product_data(self):
        """Coleta os dados dos campos do formulário."""
        # Validação básica (pode ser expandida)
        if not self.nome_produto_input.text().strip():
            QMessageBox.warning(self, "Campo Obrigatório", "O nome do produto não pode estar vazio.")
            return None
        if self.categoria_combobox.currentIndex() == 0 and self.categoria_combobox.itemData(0) is None: # "Selecione..."
             QMessageBox.warning(self, "Campo Obrigatório", "Por favor, selecione uma categoria.")
             return None
        if self.categoria_combobox.itemData(self.categoria_combobox.currentIndex()) is None: # "Carregando" ou "Erro"
             QMessageBox.warning(self, "Erro Categoria", "Categoria inválida ou não carregada.")
             return None

        return {
            "nomeProduto": self.nome_produto_input.text().strip(),
            "codigoBarras": self.codigo_barras_input.text().strip() or None, # Envia None se vazio
            "descricao": self.descricao_input.toPlainText().strip(),
            "valorUnitario": str(self.valor_unitario_spinbox.value()), # Envia como string para a API (DecimalField aceita)
            "quantidadeEstoque": self.quantidade_estoque_spinbox.value(),
            "plataforma": self.plataforma_input.text().strip() or None,
            "prazoGarantia": self.garantia_input.text().strip() or None,
            "categoria_id": self.categoria_combobox.currentData() # Pega o ID da categoria armazenado
        }

    def handle_save(self):
        """Chamado quando o botão Salvar é clicado."""
        product_payload = self.get_product_data()
        if product_payload:
            # A lógica de chamar product_service.create_product ou update_product
            # será feita no ProductWidget após o diálogo ser aceito.
            # Aqui, apenas sinalizamos que os dados são válidos e o diálogo pode ser fechado.
            print(f"AddEditProductDialog: Dados coletados para salvar: {product_payload}") # Debug
            self.accept() # Fecha o diálogo e sinaliza QDialog.Accepted
        # else: O get_product_data já mostrou o QMessageBox de aviso.


# Bloco para testar o AddEditProductDialog isoladamente
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    from state_manager.app_state import current_app_state
    # Simular login para que get_categories possa pegar o token
    current_app_state.set_user_info("test_dialog_user", user_id=99, groups=["ESTOQUISTA"])
    current_app_state.set_auth_tokens("fake_access_for_dialog_test", "fake_refresh_for_dialog_test") # Use um token real se a API estiver rodando

    app = QApplication(sys.argv)

    # Teste 1: Adicionar novo produto (sem product_data)
    print("\n--- Testando diálogo para ADICIONAR produto ---")
    add_dialog = AddEditProductDialog()
    if add_dialog.exec_() == QDialog.Accepted:
        print("ADICIONAR: Diálogo aceito. Dados coletados:", add_dialog.get_product_data())
    else:
        print("ADICIONAR: Diálogo cancelado.")

    # Teste 2: Editar produto (com product_data simulado)
    print("\n--- Testando diálogo para EDITAR produto ---")
    # Simular dados de um produto existente (incluindo o formato da categoria como a API retorna)
    # Certifique-se que o ID da categoria (ex: 1) existe nas categorias carregadas
    # e que o ProductSerializer na API retorna 'categoria' como um objeto com 'id' e 'nomeCategoria'
    produto_exemplo_para_editar = {
        "idProduto": 101,
        "nomeProduto": "Produto Exemplo Edit",
        "codigoBarras": "12345EDIT",
        "descricao": "Descrição de exemplo para edição.",
        "valorUnitario": "19.99",
        "quantidadeEstoque": 5,
        "plataforma": "PC_EDIT",
        "prazoGarantia": "1 ano EDIT",
        "categoria": {"id": 1, "nomeCategoria": "Jogos PS5"} # Simula o objeto categoria retornado pela API
    }
    # Para que populate_fields funcione corretamente, as categorias devem ser carregadas primeiro.
    # No teste isolado, get_categories() é chamado no __init__ do diálogo.
    # Se o servidor Django não estiver rodando, get_categories() falhará e o combobox não será populado.

    edit_dialog = AddEditProductDialog(product_data=produto_exemplo_para_editar)
    if edit_dialog.exec_() == QDialog.Accepted:
        print("EDITAR: Diálogo aceito. Dados coletados:", edit_dialog.get_product_data())
    else:
        print("EDITAR: Diálogo cancelado.")

    current_app_state.clear_auth_state()
    sys.exit(0)