from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet,
    GroupViewSet,
    CategoriaProdutoViewSet,
    ProdutoViewSet,
    ClienteViewSet,
    VendaViewSet
)

# Cria uma instância do DefaultRouter.
# O Router gera automaticamente as URLs para os ViewSets.
router = DefaultRouter()

# Registra cada ViewSet com o router, definindo o prefixo da URL.
# Exemplo: 'usuarios' será acessível em /api/usuarios/
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'grupos', GroupViewSet, basename='grupo')
router.register(r'categorias', CategoriaProdutoViewSet, basename='categoriaproduto')
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'vendas', VendaViewSet, basename='venda')

# As urlpatterns da API são agora determinadas automaticamente pelo router.
urlpatterns = [
    # Inclui todas as URLs geradas pelo router.
    path('', include(router.urls)),
]