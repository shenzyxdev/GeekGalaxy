# vendas_api/views.py

from rest_framework import viewsets, permissions, status, filters # Adicionado filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Group
from django.db import transaction # Para operações atômicas no banco de dados

from .models import Usuario, CategoriaProduto, Produto, Cliente, Venda, ItemVenda
from .serializers import (
    UsuarioSerializer, GroupSerializer, CategoriaProdutoSerializer,
    ProdutoSerializer, ClienteSerializer, VendaSerializer
    # ItemVendaSerializer não precisa ser importado aqui se não tiver um ViewSet próprio
)

# --- Permissões Customizadas ---
class IsAdminOrSupervisor(permissions.BasePermission):
    """
    Permite acesso apenas a Admin (superuser do Django) ou usuários no grupo SUPERVISOR.
    """
    def has_permission(self, request, view):
        # request.user.is_staff pode ser usado para administradores que podem acessar o /admin/
        # request.user.is_superuser é para superusuários
        return request.user and (request.user.is_superuser or request.user.groups.filter(name='SUPERVISOR').exists())

class IsSupervisorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.groups.filter(name='SUPERVISOR').exists())

class IsEstoquistaUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='ESTOQUISTA').exists()

class IsAtendenteUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='ATENDENTE').exists()

# --- ViewSets ---

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    # Permissão base: Apenas Admin (superuser) ou Supervisor podem listar/ver todos os usuários.
    # Criação/Edição/Deleção terá permissões mais granulares nos métodos ou no serializer.
    permission_classes = [IsAdminOrSupervisor]

    def get_serializer_context(self):
        """Passa o request para o serializer."""
        return {'request': self.request}

    def perform_create(self, serializer):
        """Garante que a senha seja obrigatória na criação."""
        password = self.request.data.get('password')
        if not password:
            # No DRF, é melhor levantar ValidationError no serializer.
            # Mas podemos fazer uma checagem aqui também.
            # Idealmente, o serializer teria password como required=True para create.
            # Como está required=False, precisamos dessa checagem.
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'password': ['Este campo é obrigatório para criar um usuário.']})
        serializer.save() # O serializer.create() já lida com o hashing da senha e grupos

    def perform_update(self, serializer):
        # O serializer.update() já tem lógicas de segurança e lida com senha/grupos
        serializer.save()

    # A action 'me' permanece a mesma
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='me', name='Get Current User Details')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # (Opcional) Action para um supervisor atribuir/modificar grupos de um usuário não-superuser
    @action(detail=True, methods=['post'], permission_classes=[IsSupervisorUser], url_path='set-groups', name='Set User Groups')
    def set_user_groups(self, request, pk=None):
        user_to_modify = self.get_object()
        current_user = request.user

        # Um supervisor não pode modificar grupos de um superusuário ou de outro supervisor (a menos que a lógica permita)
        if user_to_modify.is_superuser or (user_to_modify.groups.filter(name='SUPERVISOR').exists() and user_to_modify != current_user):
            if not current_user.is_superuser: # Apenas um superuser pode modificar outro superuser/supervisor
                return Response({'detail': 'Você não tem permissão para modificar os grupos deste usuário.'},
                                status=status.HTTP_403_FORBIDDEN)

        group_ids = request.data.get('groups_ids', None)
        if group_ids is None: # Se 'groups_ids' não for enviado, não faz nada ou retorna erro
             return Response({'detail': "Forneça 'groups_ids' (lista de IDs de grupo)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # groups_ids deve ser uma lista de inteiros
            valid_group_ids = [int(gid) for gid in group_ids]
            user_to_modify.groups.set(valid_group_ids)
            return Response({'status': 'Grupos do usuário atualizados com sucesso.'}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'detail': "IDs de grupo inválidos. Devem ser inteiros."}, status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response({'detail': "Um ou mais IDs de grupo não existem."}, status=status.HTTP_400_BAD_REQUEST)

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar Grupos (apenas leitura).
    Útil para o front-end saber quais grupos existem.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated] # Qualquer usuário autenticado pode ver os grupos

class CategoriaProdutoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProduto.objects.all().order_by('nomeCategoria')
    serializer_class = CategoriaProdutoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']: # Todos autenticados podem ver
            permission_classes = [permissions.IsAuthenticated]
        else: # Apenas Supervisor ou Estoquista podem criar, editar, deletar
              # (e Admin/Superuser por causa da herança em IsAdminOrSupervisor)
            permission_classes = [IsSupervisorUser | IsEstoquistaUser]
        return [permission() for permission in permission_classes]

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all().order_by('nomeProduto')
    serializer_class = ProdutoSerializer
    # Configurações para filtros da API
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nomeProduto', 'codigoBarras', 'descricao', 'plataforma'] # Campos para busca ?search=termo
    ordering_fields = ['nomeProduto', 'valorUnitario', 'quantidadeEstoque', 'idCategoria__nomeCategoria'] # Campos para ?ordering=campo

    def get_permissions(self):
        if self.action in ['list', 'retrieve']: # Todos autenticados podem ver
            permission_classes = [permissions.IsAuthenticated]
        else: # Apenas Supervisor ou Estoquista podem criar, editar, deletar
            permission_classes = [IsSupervisorUser | IsEstoquistaUser]
        return [permission() for permission in permission_classes]

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('nome')
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'cpf', 'email', 'cidade']
    ordering_fields = ['nome', 'dataCadastro', 'cidade']


    def get_permissions(self):
        if self.action in ['list', 'retrieve']: # Todos autenticados podem ver
            permission_classes = [permissions.IsAuthenticated]
        else: # Apenas Supervisor ou Atendente podem criar, editar, deletar
            permission_classes = [IsSupervisorUser | IsAtendenteUser]
        return [permission() for permission in permission_classes]

class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all().order_by('-dataHoraVenda')
    serializer_class = VendaSerializer
    filter_backends = [filters.OrderingFilter] # Poderia adicionar SearchFilter se necessário
    ordering_fields = ['dataHoraVenda', 'valorTotalVenda', 'statusVenda', 'cliente__nome', 'usuario__username']


    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAtendenteUser | IsSupervisorUser]
        elif self.action in ['update', 'partial_update']: # Para cancelar venda
            permission_classes = [IsSupervisorUser]
        elif self.action == 'destroy': # Não recomendado deletar vendas, apenas cancelar
            permission_classes = [IsAdminOrSupervisor] # Apenas admin ou supervisor
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminOrSupervisor] # Padrão mais restritivo
        return [permission() for permission in permission_classes]

    @transaction.atomic
    def perform_create(self, serializer):
        # O serializer VendaSerializer já tem a lógica para:
        # - Criar os ItensVenda
        # - Decrementar o estoque dos Produtos
        # - Calcular o valorTotalVenda
        serializer.save(usuario=self.request.user) # Associa o usuário logado à venda

    @transaction.atomic
    def perform_update(self, serializer):
        # O serializer VendaSerializer já tem a lógica para:
        # - Estornar o estoque se a venda for CANCELADA
        # - Simular comunicação com sistema financeiro (via print)
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsSupervisorUser], url_path='autorizar-excluir-item', name='Autorizar Exclusao Item Venda')
    def autorizar_exclusao_item(self, request, pk=None):
        """
        RF015: Supervisor autoriza a exclusão de um item de uma venda (geralmente venda EM_ABERTO).
        Espera 'item_venda_id' no corpo do request.data.
        """
        venda = self.get_object()
        item_venda_id_str = request.data.get('item_venda_id')

        if not item_venda_id_str:
            return Response({'detail': 'ID do item da venda (item_venda_id) não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            item_venda_id = int(item_venda_id_str) # Garante que é um inteiro
        except ValueError:
            return Response({'detail': 'ID do item da venda inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # O ItemVenda tem 'id' como PK automática se não definimos outra.
            # Precisamos garantir que nosso modelo ItemVenda realmente tem 'id' como PK.
            # Se ItemVenda usa chave composta ou outra PK, ajuste aqui.
            # Vamos assumir que ItemVenda tem um 'id' (AutoField) como PK.
            # No nosso models.py, ItemVenda não tinha um ID explícito, então Django cria 'id'.
            item_para_excluir = ItemVenda.objects.get(id=item_venda_id, venda=venda)
        except ItemVenda.DoesNotExist:
            return Response({'detail': 'Item não encontrado nesta venda ou ID do item inválido.'}, status=status.HTTP_404_NOT_FOUND)
        except ItemVenda.MultipleObjectsReturned: # Segurança
             return Response({'detail': 'Múltiplos itens encontrados com este ID, verifique os dados.'}, status=status.HTTP_400_BAD_REQUEST)


        # RF008 - Estornar quantidade para o estoque
        produto_original = item_para_excluir.produto
        produto_original.quantidadeEstoque += item_para_excluir.quantidade
        produto_original.save()

        # Remover o item e recalcular o total da venda
        valor_item_excluido = item_para_excluir.subtotal # Usa a property @subtotal
        item_para_excluir.delete() # Exclui o objeto ItemVenda

        # Recalcula o valorTotalVenda
        novo_total_venda = 0
        for item_restante in venda.itens.all(): # venda.itens é o related_name
            novo_total_venda += item_restante.subtotal
        
        venda.valorTotalVenda = novo_total_venda
        venda.save()

        # Retorna a venda atualizada
        serializer = self.get_serializer(venda)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Não é necessário um ViewSet para ItemVenda se eles são gerenciados
# exclusivamente através do nested serializer do VendaViewSet.