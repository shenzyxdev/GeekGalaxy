# desktop_app/ui/add_edit_client_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QDialogButtonBox)
from PyQt5.QtCore import Qt

class AddEditClientDialog(QDialog):
    def __init__(self, client_data=None, parent=None):
        super().__init__(parent)

        self.client_data_to_edit = client_data
        self.is_edit_mode = bool(client_data)

        self.setWindowTitle("Adicionar Novo Cliente" if not self.is_edit_mode else "Editar Cliente")
        self.setMinimumWidth(450)
        self.setModal(True)

        self.init_ui()

        if self.is_edit_mode:
            self.populate_fields()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Campos do formulário (baseado no modelo Cliente e PIM)
        self.nome_input = QLineEdit(self)
        self.cpf_input = QLineEdit(self)
        self.cpf_input.setPlaceholderText("000.000.000-00") # Pode adicionar QInputMask depois
        self.rg_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("exemplo@dominio.com")
        self.telefone_input = QLineEdit(self)
        self.telefone_input.setPlaceholderText("(00) 00000-0000")

        self.logradouro_input = QLineEdit(self)
        self.numero_input = QLineEdit(self)
        self.complemento_input = QLineEdit(self)
        self.bairro_input = QLineEdit(self)
        self.cidade_input = QLineEdit(self)
        self.uf_input = QLineEdit(self)
        self.uf_input.setMaxLength(2) # UF tem 2 caracteres
        self.cep_input = QLineEdit(self)
        self.cep_input.setPlaceholderText("00000-000")

        form_layout.addRow(QLabel("Nome Completo:"), self.nome_input)
        form_layout.addRow(QLabel("CPF:"), self.cpf_input)
        form_layout.addRow(QLabel("RG:"), self.rg_input)
        form_layout.addRow(QLabel("E-mail:"), self.email_input)
        form_layout.addRow(QLabel("Telefone:"), self.telefone_input)
        form_layout.addRow(QLabel("Logradouro (Rua, Av.):"), self.logradouro_input)
        form_layout.addRow(QLabel("Número:"), self.numero_input)
        form_layout.addRow(QLabel("Complemento:"), self.complemento_input)
        form_layout.addRow(QLabel("Bairro:"), self.bairro_input)
        form_layout.addRow(QLabel("Cidade:"), self.cidade_input)
        form_layout.addRow(QLabel("UF:"), self.uf_input)
        form_layout.addRow(QLabel("CEP:"), self.cep_input)

        main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.button_box.button(QDialogButtonBox.Save).setText("Salvar")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Cancelar")
        self.button_box.accepted.connect(self.handle_save)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def populate_fields(self):
        if not self.client_data_to_edit:
            return

        self.nome_input.setText(self.client_data_to_edit.get('nome', ''))
        self.cpf_input.setText(self.client_data_to_edit.get('cpf', ''))
        self.rg_input.setText(self.client_data_to_edit.get('rg', ''))
        self.email_input.setText(self.client_data_to_edit.get('email', ''))
        self.telefone_input.setText(self.client_data_to_edit.get('telefone', ''))
        self.logradouro_input.setText(self.client_data_to_edit.get('logradouro', ''))
        self.numero_input.setText(self.client_data_to_edit.get('numero', ''))
        self.complemento_input.setText(self.client_data_to_edit.get('complemento', ''))
        self.bairro_input.setText(self.client_data_to_edit.get('bairro', ''))
        self.cidade_input.setText(self.client_data_to_edit.get('cidade', ''))
        self.uf_input.setText(self.client_data_to_edit.get('uf', ''))
        self.cep_input.setText(self.client_data_to_edit.get('cep', ''))
        print("AddEditClientDialog: Campos populados para edição.")

    def get_client_data(self):
        # Validação básica
        nome = self.nome_input.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo Obrigatório", "O nome do cliente não pode estar vazio.")
            return None
        # Adicionar mais validações se necessário (ex: formato de CPF, e-mail)

        return {
            "nome": nome,
            "cpf": self.cpf_input.text().strip() or None,
            "rg": self.rg_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "telefone": self.telefone_input.text().strip() or None,
            "logradouro": self.logradouro_input.text().strip() or None,
            "numero": self.numero_input.text().strip() or None,
            "complemento": self.complemento_input.text().strip() or None,
            "bairro": self.bairro_input.text().strip() or None,
            "cidade": self.cidade_input.text().strip() or None,
            "uf": self.uf_input.text().strip().upper() or None,
            "cep": self.cep_input.text().strip() or None,
        }

    def handle_save(self):
        client_payload = self.get_client_data()
        if client_payload:
            print(f"AddEditClientDialog: Dados coletados para salvar: {client_payload}")
            self.accept()

# Bloco para testar o AddEditClientDialog isoladamente
if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    # Não precisamos do AppState para este teste isolado simples do diálogo
    # a menos que o diálogo precise de alguma informação global.

    app = QApplication(sys.argv)

    # Teste Adicionar
    print("\n--- Testando diálogo para ADICIONAR cliente ---")
    add_dialog_client = AddEditClientDialog()
    if add_dialog_client.exec_() == QDialog.Accepted:
        print("ADICIONAR CLIENTE: Diálogo aceito. Dados:", add_dialog_client.get_client_data())
    else:
        print("ADICIONAR CLIENTE: Diálogo cancelado.")

    # Teste Editar
    print("\n--- Testando diálogo para EDITAR cliente ---")
    cliente_exemplo = {
        "id": 1, "nome": "Cliente Teste Antigo", "cpf": "123.456.789-00", "email": "teste@teste.com"
        # ... preencher outros campos se necessário para o teste
    }
    edit_dialog_client = AddEditClientDialog(client_data=cliente_exemplo)
    if edit_dialog_client.exec_() == QDialog.Accepted:
        print("EDITAR CLIENTE: Diálogo aceito. Dados:", edit_dialog_client.get_client_data())
    else:
        print("EDITAR CLIENTE: Diálogo cancelado.")
    sys.exit(0)