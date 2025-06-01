from rest_framework import serializers
from django.contrib.auth.models import Group # Para serializar os grupos de usuários
from .models import Usuario, CategoriaProduto, Produto, Cliente, Venda, ItemVenda

# Serializer para o modelo Group (para mostrar os grupos do usuário)
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name') # <<< VERIFIQUE E CORRIJA ESTA LINHA

# Serializer para o nosso modelo Usuario customizado
class UsuarioSerializer(serializers.ModelSerializer):
    # groups = GroupSerializer(many=True, read_only=True) # Bom para leitura
    # Para escrita (criação/atualização), precisamos aceitar uma lista de IDs de grupo
    groups_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        write_only=True, # Apenas para entrada de dados
        required=False, # Grupos são opcionais
        source='groups' # Mapeia para o campo 'groups' do modelo ao salvar
    )
    # Para leitura, manteremos a representação aninhada dos grupos
    groups = GroupSerializer(many=True, read_only=True)

    password = serializers.CharField(
        write_only=True,
        required=False, # Não obrigatório em updates, mas sim em creates (tratado na view ou create)
        style={'input_type': 'password'}
    )

    class Meta:
        model = Usuario
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', # Para entrada
            'groups',   # Para leitura (nomes dos grupos)
            'groups_ids', # Para escrita (lista de IDs de grupo)
            'is_staff', 'is_active', 'is_superuser' # is_superuser será read_only para não-superusers
        )
        read_only_fields = ('id', 'is_superuser') # Por padrão, is_superuser não deve ser editável por não-superusers
                                                  # 'groups' já é read_only pela definição acima

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', None) # 'groups' aqui vem de 'groups_ids' por causa do source
        password = validated_data.pop('password', None)

        # Não permitir que um não-superuser crie um superuser ou staff
        request = self.context.get('request')
        if request and not request.user.is_superuser:
            validated_data['is_superuser'] = False
            # validated_data['is_staff'] = False # Decida se supervisor pode criar staff

        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        if groups_data:
            user.groups.set(groups_data)
        return user

    def update(self, instance, validated_data):
        groups_data = validated_data.pop('groups', None) # Vem de 'groups_ids'
        password = validated_data.pop('password', None)

        # Lógica de segurança:
        request = self.context.get('request')
        current_user = request.user if request else None

        # Não permitir que um supervisor edite um superusuário, a menos que seja ele mesmo (improvável)
        # ou que um supervisor altere o status de superusuário.
        if instance.is_superuser and (not current_user or not current_user.is_superuser):
            raise serializers.ValidationError("Você não tem permissão para editar um superusuário.")

        # Não permitir que um supervisor se promova a superusuário ou promova outros
        if 'is_superuser' in validated_data and (not current_user or not current_user.is_superuser):
            validated_data.pop('is_superuser') # Remove a tentativa de alteração

        # Não permitir que um supervisor altere o status 'is_staff' de outros (a menos que seja permitido)
        # if 'is_staff' in validated_data and (not current_user or not current_user.is_superuser):
        #     validated_data.pop('is_staff')

        # Atualiza os campos do usuário
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password) # set_password faz o hashing

        instance.save()

        if groups_data is not None: # Permite limpar os grupos se uma lista vazia for enviada
            instance.groups.set(groups_data)
        return instance

    def update(self, instance, validated_data):
        # Lógica para atualizar um usuário, incluindo a senha se fornecida
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password) # set_password hasheia a senha

        instance.save()
        return instance

class CategoriaProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProduto
        fields = '__all__' # Inclui todos os campos do modelo

class ProdutoSerializer(serializers.ModelSerializer):
    # Para mostrar o nome da categoria ao invés de apenas o ID
    # categoria_nome = serializers.CharField(source='categoria.nomeCategoria', read_only=True)
    # Ou, se quisermos que o campo 'categoria' no POST/PUT seja o ID, mas no GET mostre detalhes:
    categoria = CategoriaProdutoSerializer(read_only=True) # No GET, mostra o objeto categoria serializado
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaProduto.objects.all(), source='categoria', write_only=True
    ) # No POST/PUT, espera um ID para categoria

    class Meta:
        model = Produto
        fields = (
            'id', 'codigoBarras', 'nomeProduto', 'descricao', 'valorUnitario',
            'quantidadeEstoque', 'plataforma', 'prazoGarantia',
            'categoria', 'categoria_id' # Inclui ambos para leitura e escrita
        )
        # Se quisermos um campo específico para POST/PUT e outro para GET,
        # podemos nomeá-los diferentemente ou usar customizações.
        # O método acima com 'categoria' (read_only) e 'categoria_id' (write_only) é uma abordagem.

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

# Serializer para ItemVenda, será usado dentro do VendaSerializer (nested)
class ItemVendaSerializer(serializers.ModelSerializer):
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source='produto' # Para escrita, espera o ID do produto
    )
    # Para leitura, podemos incluir detalhes do produto
    produto = ProdutoSerializer(read_only=True)
    subtotal_calculado = serializers.DecimalField(source='subtotal', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemVenda
        # 'venda' será gerenciado pelo VendaSerializer, não precisa estar aqui para escrita
        fields = ('id', 'produto_id', 'produto', 'quantidade', 'precoUnitarioVenda', 'subtotal_calculado')
        read_only_fields = ('id', 'produto', 'subtotal_calculado')


class VendaSerializer(serializers.ModelSerializer):
    # Usando nested serializer para mostrar/criar os itens da venda
    itens = ItemVendaSerializer(many=True)
    # Para mostrar nomes ao invés de apenas IDs
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True, allow_null=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    # Para permitir a criação de uma venda associada a um cliente existente pelo ID
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Venda
        fields = (
            'id', 'dataHoraVenda', 'cliente_id', 'cliente_nome', 'usuario_username',
            'formaPagamento', 'statusPagamento', 'statusVenda', 'valorTotalVenda', 'itens'
        )
        # dataHoraVenda é auto_now_add, valorTotalVenda será calculado, usuario será o logado
        read_only_fields = ('id', 'dataHoraVenda', 'usuario_username', 'valorTotalVenda')

    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        # 'cliente' já foi tratado pelo source='cliente' no cliente_id e será passado em validated_data
        # 'usuario' será atribuído na view com base no request.user

        # Cria a instância da venda
        venda = Venda.objects.create(**validated_data)

        valor_total_calculado = 0
        for item_data in itens_data:
            produto_obj = item_data['produto'] # 'produto' aqui é o objeto Produto, pois source='produto' no produto_id
            quantidade_vendida = item_data['quantidade']
            preco_unitario = item_data.get('precoUnitarioVenda', produto_obj.valorUnitario) # Pega preço do request ou do produto

            # Verificar estoque (RF008 - parte da lógica)
            if produto_obj.quantidadeEstoque < quantidade_vendida:
                raise serializers.ValidationError(
                    f"Estoque insuficiente para o produto '{produto_obj.nomeProduto}'. "
                    f"Disponível: {produto_obj.quantidadeEstoque}, Solicitado: {quantidade_vendida}."
                )

            # Criar o ItemVenda
            item = ItemVenda.objects.create(
                venda=venda,
                produto=produto_obj,
                quantidade=quantidade_vendida,
                precoUnitarioVenda=preco_unitario
            )
            valor_total_calculado += item.subtotal

            # Atualizar estoque do produto (RF008)
            produto_obj.quantidadeEstoque -= quantidade_vendida
            produto_obj.save()

        venda.valorTotalVenda = valor_total_calculado
        venda.save()
        return venda

    def update(self, instance, validated_data):
        # Lógica para atualizar venda, especialmente para cancelamento (RF016)
        # O statusVenda virá em validated_data se estiver sendo alterado

        # Salva outras alterações primeiro
        # Itens não são atualizados desta forma simples, geralmente se remove/adiciona
        # ou se tem um endpoint específico para itens.
        # Para cancelamento, focamos no statusVenda.
        itens_data = validated_data.pop('itens', None) # Não vamos processar atualização de itens aqui

        # Se o status da venda está mudando para 'CANCELADA' e não era 'CANCELADA' antes
        novo_status_venda = validated_data.get('statusVenda', instance.statusVenda)
        if novo_status_venda == 'CANCELADA' and instance.statusVenda != 'CANCELADA':
            # Estornar itens ao estoque
            for item_venda in instance.itens.all():
                produto = item_venda.produto
                produto.quantidadeEstoque += item_venda.quantidade
                produto.save()
            # RF017 - Simular comunicação com sistema financeiro
            print(f"LOG: Venda {instance.id} cancelada. Código enviado ao sistema financeiro.")
            instance.statusPagamento = 'CANCELADO_ESTORNADO' # Ou um status apropriado

        instance.formaPagamento = validated_data.get('formaPagamento', instance.formaPagamento)
        instance.statusPagamento = validated_data.get('statusPagamento', instance.statusPagamento)
        instance.statusVenda = novo_status_venda
        # Outros campos da venda podem ser atualizados aqui se necessário

        instance.save()
        return instance