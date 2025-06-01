# desktop_app/ui/receipt_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit,
                             QPushButton, QDialogButtonBox, QGridLayout, QSizePolicy, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

class ReceiptDialog(QDialog):
    def __init__(self, sale_data, parent=None):
        """
        Construtor do diálogo de recibo.
        sale_data: Dicionário com os dados da venda finalizada.
        """
        super().__init__(parent)
        self.sale_data = sale_data

        self.setWindowTitle(f"Comprovante de Venda - #{self.sale_data.get('id', 'N/A')}")
        self.setMinimumSize(450, 550) # Ajuste o tamanho conforme necessário
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Informações da Loja (Placeholder) ---
        store_name_label = QLabel("GeekGalaxy Store")
        store_name_label.setFont(QFont("Arial", 16, QFont.Bold))
        store_name_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(store_name_label)

        store_info_label = QLabel("CNPJ: XX.XXX.XXX/0001-XX - Endereço da Loja Placeholder\nTelefone: (XX) XXXX-XXXX")
        store_info_label.setAlignment(Qt.AlignCenter)
        store_info_label.setStyleSheet("font-size: 9px; margin-bottom: 10px;")
        main_layout.addWidget(store_info_label)

        # --- Detalhes da Venda ---
        header_layout = QGridLayout()
        header_layout.addWidget(QLabel("<b>ID da Venda:</b>", self), 0, 0)
        header_layout.addWidget(QLabel(str(self.sale_data.get('id', 'N/A')), self), 0, 1)

        data_hora_str = self.sale_data.get('dataHoraVenda', 'N/A')
        data_formatada = data_hora_str # Fallback
        try:
            # Tenta formatar a data/hora de forma mais robusta
            if 'T' in data_hora_str:
                date_part_str = data_hora_str.split("T")[0]
                time_part_str = data_hora_str.split("T")[1].split(".")[0][:5] # HH:mm
                # Tenta converter a parte da data
                dt_obj = QDate.fromString(date_part_str, Qt.ISODate)
                if dt_obj.isValid():
                     data_formatada = dt_obj.toString("dd/MM/yyyy") + " às " + time_part_str
                else: # Se a data não for válida no formato ISO, usa como está
                    data_formatada = f"{date_part_str} {time_part_str}"
        except Exception as e:
            print(f"Erro ao formatar data do recibo: {e}")
            # data_formatada permanece como o valor original se houver erro
            
        header_layout.addWidget(QLabel("<b>Data/Hora:</b>", self), 1, 0)
        header_layout.addWidget(QLabel(data_formatada, self), 1, 1)

        header_layout.addWidget(QLabel("<b>Cliente:</b>", self), 0, 2)
        header_layout.addWidget(QLabel(self.sale_data.get('cliente_nome', 'Não Identificado'), self), 0, 3)

        header_layout.addWidget(QLabel("<b>Vendedor:</b>", self), 1, 2)
        header_layout.addWidget(QLabel(self.sale_data.get('usuario_username', 'N/A'), self), 1, 3)
        
        header_layout.setColumnStretch(1, 1) # Dá mais espaço para os valores
        header_layout.setColumnStretch(3, 1)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(10)

        # --- Itens da Venda ---
        items_label = QLabel("<b>Itens Comprados:</b>", self)
        main_layout.addWidget(items_label)

        self.items_text_edit = QTextEdit(self)
        self.items_text_edit.setReadOnly(True)
        self.items_text_edit.setFontFamily("Courier New") # Fonte monoespaçada para alinhamento
        self.items_text_edit.setMinimumHeight(150) # Ajuste conforme necessidade

        # Monta o texto dos itens
        items_header = "{:<28} {:>5} {:>10} {:>12}\n".format("Produto", "Qtd", "Preço Uni.", "Subtotal")
        items_header += "=" * 58 + "\n" # Linha separadora
        items_str_list = [items_header]

        for item in self.sale_data.get('itens', []):
            # O VendaSerializer retorna 'itens' com ItemVendaSerializer,
            # que tem 'produto' (nested ProdutoSerializer) e 'precoUnitarioVenda'.
            # 'subtotal_calculado' foi adicionado como @property no modelo ItemVenda e serializado.
            product_info = item.get('produto', {}) # produto é um dict aninhado
            product_name = product_info.get('nomeProduto', 'Produto Desconhecido')
            
            quantity = item.get('quantidade', 0)
            unit_price = float(item.get('precoUnitarioVenda', 0.0))
            # O subtotal do item já deve vir calculado pelo ItemVendaSerializer (subtotal_calculado)
            # ou podemos calcular aqui: quantity * unit_price
            subtotal_item = float(item.get('subtotal_calculado', quantity * unit_price))

            # Limita o nome do produto para evitar quebra de layout
            product_name_display = (product_name[:25] + '...') if len(product_name) > 28 else product_name

            items_str_list.append("{:<28.28} {:>5} {:>10.2f} {:>12.2f}".format(
                product_name_display, quantity, unit_price, subtotal_item
            ))
        self.items_text_edit.setText("\n".join(items_str_list))
        main_layout.addWidget(self.items_text_edit)
        main_layout.addSpacing(10)

        # --- Totais e Pagamento (Definindo summary_layout aqui) ---
        summary_layout = QGridLayout() # DEFINIDO AQUI
        total_label = QLabel("<b>TOTAL DA VENDA:</b>", self)
        total_label.setFont(QFont("Arial", 12, QFont.Bold))
        summary_layout.addWidget(total_label, 0, 0, Qt.AlignRight)
        
        total_value_label = QLabel(f"<b>R$ {float(self.sale_data.get('valorTotalVenda', 0.0)):.2f}</b>", self)
        total_value_label.setFont(QFont("Arial", 12, QFont.Bold))
        total_value_label.setStyleSheet("color: green;")
        summary_layout.addWidget(total_value_label, 0, 1, Qt.AlignRight)

        summary_layout.addWidget(QLabel("Forma de Pagamento:", self), 1, 0, Qt.AlignRight)
        # Formata o nome da forma de pagamento para melhor leitura
        forma_pgto_str = str(self.sale_data.get('formaPagamento', 'N/A')).replace("_", " ").title()
        summary_layout.addWidget(QLabel(forma_pgto_str, self), 1, 1, Qt.AlignRight)
        
        summary_layout.setColumnStretch(0,1) # Empurra para a direita
        main_layout.addLayout(summary_layout) # ADICIONADO AO main_layout
        main_layout.addStretch()

        # --- Botões ---
        self.button_box = QDialogButtonBox(self)
        # Adiciona o botão "Imprimir"
        print_button = self.button_box.addButton("Imprimir Recibo", QDialogButtonBox.ActionRole)
        # Adiciona o botão "Fechar" como o botão OK padrão
        close_button = self.button_box.addButton("Fechar Comprovante", QDialogButtonBox.AcceptRole) # Ou .RejectRole se preferir

        print_button.clicked.connect(self.handle_print_receipt)
        self.button_box.accepted.connect(self.accept) # Conectado ao botão com AcceptRole
        # Se usou RejectRole para fechar: self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def handle_print_receipt(self):
        print("ReceiptDialog: Botão Imprimir clicado.")
        
        receipt_text = f"      GEEKGALAXY STORE\n"
        receipt_text += f"CNPJ: XX.XXX.XXX/0001-XX\n"
        receipt_text += f"Endereço da Loja Placeholder\n"
        receipt_text += f"Telefone: (XX) XXXX-XXXX\n"
        receipt_text += "=" * 40 + "\n"
        receipt_text += f"COMPROVANTE DE VENDA #{self.sale_data.get('id', 'N/A')}\n"
        
        data_hora_str = self.sale_data.get('dataHoraVenda', 'N/A')
        data_formatada_recibo = data_hora_str
        try:
            if 'T' in data_hora_str:
                date_part_str = data_hora_str.split("T")[0]
                time_part_str = data_hora_str.split("T")[1].split(".")[0][:5]
                dt_obj = QDate.fromString(date_part_str, Qt.ISODate)
                if dt_obj.isValid(): data_formatada_recibo = dt_obj.toString("dd/MM/yyyy") + " " + time_part_str
                else: data_formatada_recibo = f"{date_part_str} {time_part_str}"
        except: pass
        receipt_text += f"Data: {data_formatada_recibo}\n"
        receipt_text += f"Cliente: {self.sale_data.get('cliente_nome', 'Não Identificado')}\n"
        receipt_text += f"Vendedor: {self.sale_data.get('usuario_username', 'N/A')}\n"
        receipt_text += "-" * 40 + "\n"
        receipt_text += "{:<18} {:>3} {:>8} {:>10}\n".format("Produto", "Qtd", "V.Uni", "Subtotal")
        receipt_text += "-" * 40 + "\n"

        for item in self.sale_data.get('itens', []):
            product_info = item.get('produto', {})
            product_name = product_info.get('nomeProduto', 'Prod Desc.')
            quantity = item.get('quantidade', 0)
            unit_price = float(item.get('precoUnitarioVenda', 0.0))
            subtotal_item = float(item.get('subtotal_calculado', quantity * unit_price))
            
            product_name_display = (product_name[:15] + "..") if len(product_name) > 17 else product_name
            receipt_text += "{:<18.18} {:>3} {:>8.2f} {:>10.2f}\n".format(
                product_name_display, quantity, unit_price, subtotal_item
            )
        
        receipt_text += "-" * 40 + "\n"
        receipt_text += "{:>31} {:>10.2f}\n".format("TOTAL R$:", float(self.sale_data.get('valorTotalVenda', 0.0)))
        forma_pgto_str = str(self.sale_data.get('formaPagamento', 'N/A')).replace("_", " ").title()
        receipt_text += f"Forma Pagamento: {forma_pgto_str}\n"
        receipt_text += "-" * 40 + "\n"
        receipt_text += "      Obrigado e Volte Sempre!\n"
        receipt_text += "=" * 40 + "\n"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Simulação de Impressão")
        msg_box.setText("Recibo gerado (simulação):")
        # Para exibir o texto formatado corretamente, usamos um QLabel com rich text ou um QTextEdit
        detailed_text_widget = QTextEdit()
        detailed_text_widget.setReadOnly(True)
        detailed_text_widget.setFontFamily("Courier New")
        detailed_text_widget.setPlainText(receipt_text)
        detailed_text_widget.setMinimumHeight(300) # Altura para o texto
        detailed_text_widget.setMinimumWidth(400)  # Largura para o texto

        # Adicionar o QTextEdit a um layout dentro da QMessageBox não é direto.
        # Uma alternativa é usar um QDialog customizado ou apenas o setDetailedText.
        # Para o QMessageBox, o setDetailedText é mais simples.
        msg_box.setDetailedText(receipt_text) # Mantém o texto nos detalhes

        # Tentar exibir um resumo no texto principal da QMessageBox
        summary_info = (
            f"Venda ID: {self.sale_data.get('id', 'N/A')}\n"
            f"Data: {data_formatada_recibo}\n"
            f"Total: R$ {float(self.sale_data.get('valorTotalVenda', 0.0)):.2f}\n\n"
            "Clique em 'Show Details...' para ver o recibo completo."
        )
        msg_box.setInformativeText(summary_info)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

# Bloco para testar o ReceiptDialog isoladamente
if __name__ == '__main__':
    import sys
    import os
    # QApplication já importado no topo

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_app_dir = os.path.dirname(current_script_dir)
    if desktop_app_dir not in sys.path:
        sys.path.insert(0, desktop_app_dir)

    app = QApplication(sys.argv)

    sample_sale_data = {
        'id': 101,
        'dataHoraVenda': QDate.currentDate().toString(Qt.ISODate) + "T15:30:00Z", # Formato ISO com Z
        'cliente_nome': 'Maria Oliveira Santos',
        'usuario_username': 'atendente_caixa',
        'valorTotalVenda': "239.80",
        'formaPagamento': 'CARTAO_DEBITO',
        'itens': [
            {'produto': {'nomeProduto': 'Produto A Teste Nome Muito Longo Para Caber'}, 'quantidade': 2, 'precoUnitarioVenda': "100.00", 'subtotal_calculado': "200.00"},
            {'produto': {'nomeProduto': 'Item B Curto'}, 'quantidade': 1, 'precoUnitarioVenda': "39.80", 'subtotal_calculado': "39.80"}
        ]
    }
    dialog = ReceiptDialog(sale_data=sample_sale_data)
    dialog.exec_()
    sys.exit(0)