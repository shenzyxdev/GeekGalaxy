from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission # Adicione Group e Permission aqui

class Usuario(AbstractUser):
    # Adicione os related_name para evitar conflitos
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="usuario_set", # Nome de acesso reverso customizado
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_set", # Nome de acesso reverso customizado
        related_query_name="usuario",
    )

    # O restante do seu modelo Usuario (se houver) ou 'pass'
    # pass # Se não houver mais nada

    def __str__(self):
        return self.username
class CategoriaProduto(models.Model):
    # idCategoria é criado automaticamente pelo Django como 'id' (AutoField, primary_key=True)
    # Se quisermos explicitamente nomear, faríamos:
    # idCategoria = models.AutoField(primary_key=True)
    nomeCategoria = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")

    def __str__(self):
        return self.nomeCategoria

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"

class Produto(models.Model):
    # idProduto é criado automaticamente pelo Django como 'id'
    codigoBarras = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Código de Barras")
    nomeProduto = models.CharField(max_length=255, verbose_name="Nome do Produto")
    descricao = models.TextField(null=True, blank=True, verbose_name="Descrição")
    valorUnitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Unitário (R$)")
    quantidadeEstoque = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    # Para jogos e acessórios, conforme PIM [cite: 1]
    plataforma = models.CharField(max_length=100, null=True, blank=True, verbose_name="Plataforma (Jogos/Acessórios)")
    prazoGarantia = models.CharField(max_length=100, null=True, blank=True, verbose_name="Prazo de Garantia")
    # Relacionamento ForeignKey: Um produto pertence a uma categoria.
    # Uma categoria pode ter vários produtos.
    # models.PROTECT impede que uma categoria seja deletada se houver produtos nela.
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.PROTECT, verbose_name="Categoria")
    # imagem = models.ImageField(upload_to='produtos_imagens/', null=True, blank=True) # Futuramente, se quisermos imagens

    def __str__(self):
        return self.nomeProduto

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

class Cliente(models.Model):
    # idCliente é criado automaticamente pelo Django como 'id'
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    # Conforme PIM [cite: 1]
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True, verbose_name="CPF") # Ex: 000.000.000-00
    rg = models.CharField(max_length=20, null=True, blank=True, verbose_name="RG")
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone") # Ex: (00) 90000-0000
    dataCadastro = models.DateField(auto_now_add=True, verbose_name="Data de Cadastro")

    # Endereço (Conforme PIM [cite: 1])
    logradouro = models.CharField(max_length=255, null=True, blank=True, verbose_name="Logradouro (Rua, Av.)")
    numero = models.CharField(max_length=10, null=True, blank=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, null=True, blank=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, null=True, blank=True, verbose_name="Cidade")
    uf = models.CharField(max_length=2, null=True, blank=True, verbose_name="UF") # Sigla do Estado, ex: SP
    cep = models.CharField(max_length=9, null=True, blank=True, verbose_name="CEP") # Ex: 00000-000

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Venda(models.Model):
    # idVenda é criado automaticamente pelo Django como 'id'
    STATUS_VENDA_CHOICES = [
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('EM_ABERTO', 'Em Aberto'), # Para vendas que estão sendo montadas
    ]
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('PIX', 'PIX'),
    ]
    STATUS_PAGAMENTO_CHOICES = [ # Conforme PIM [cite: 1]
        ('PAGO', 'Pago'),
        ('PENDENTE', 'Pendente'),
        ('REJEITADO', 'Rejeitado'), # Ex: transação de cartão não aprovada
    ]

    # Conforme PIM [cite: 1]
    dataHoraVenda = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora da Venda")
    valorTotalVenda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Total (R$)")
    formaPagamento = models.CharField(max_length=50, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True, verbose_name="Forma de Pagamento")
    statusPagamento = models.CharField(max_length=50, choices=STATUS_PAGAMENTO_CHOICES, default='PENDENTE', verbose_name="Status do Pagamento")
    statusVenda = models.CharField(max_length=50, choices=STATUS_VENDA_CHOICES, default='EM_ABERTO', verbose_name="Status da Venda")

    # Relacionamentos ForeignKey
    # Uma venda pode ou não ter um cliente associado (venda anônima).
    # Se o cliente for deletado, o campo idCliente na venda fica NULO.
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    # Quem realizou a venda (Atendente/Supervisor).
    # Se o usuário for deletado, a venda NÃO será deletada (PROTECT).
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='vendas_realizadas', verbose_name="Vendedor")

    def __str__(self):
        return f"Venda #{self.id} - {self.dataHoraVenda.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

class ItemVenda(models.Model):
    # idItemVenda é criado automaticamente pelo Django como 'id'
    # Relacionamentos ForeignKey
    # Um item de venda pertence a uma Venda. Se a Venda for deletada, todos os seus itens são deletados (CASCADE).
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE, verbose_name="Venda Associada")
    # Um item de venda refere-se a um Produto. Se o Produto for deletado, o item NÃO será deletado (PROTECT),
    # pois precisamos manter o histórico da venda. (Alternativa: models.SET_NULL se o produto puder ser nulo depois)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, verbose_name="Produto Vendido")

    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Vendida")
    # Preço unitário do produto NO MOMENTO DA VENDA, para histórico.
    precoUnitarioVenda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário na Venda (R$)")

    @property
    def subtotal(self):
        return self.quantidade * self.precoUnitarioVenda

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nomeProduto} (Venda #{self.venda.id})"

    class Meta:
        verbose_name = "Item de Venda"
        verbose_name_plural = "Itens de Venda"
        # Para garantir que não haja o mesmo produto duas vezes como item separado na mesma venda.
        # Se for permitido (ex: duas linhas do mesmo produto com descontos diferentes), remova isso
        # e use o 'id' autoincrementado como chave primária simples.
        # unique_together = ('venda', 'produto') # Descomente se quiser essa restrição