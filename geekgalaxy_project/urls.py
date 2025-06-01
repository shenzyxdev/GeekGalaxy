from django.contrib import admin
from django.urls import path, include # Certifique-se de que 'include' está importado
from rest_framework_simplejwt.views import ( # Importar as views para JWT
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls), # URL para a área administrativa do Django

    # Inclui as URLs do nosso app 'vendas_api'.
    # Todas as URLs definidas em 'vendas_api.urls' serão acessadas
    # começando com o prefixo 'api/'.
    # Ex: /api/produtos/, /api/clientes/, etc.
    path('api/', include('vendas_api.urls')),

    # URLs para Autenticação por Token JWT
    # O front-end enviará o nome de usuário e senha para '/api/token/'
    # para obter os tokens de acesso e atualização.
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # O front-end usará '/api/token/refresh/' para obter um novo token de acesso
    # quando o token de acesso atual expirar, usando o token de atualização.
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]