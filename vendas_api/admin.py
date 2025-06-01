from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Para customizar o admin do nosso Usuário
from .models import Usuario, CategoriaProduto, Produto, Cliente, Venda, ItemVenda

# Customizando a exibição do nosso modelo Usuario no Admin
# Se você não adicionou campos extras ao Usuario, pode ser mais simples:
# admin.site.register(Usuario, UserAdmin)
# Mas vamos criar uma classe para futuras customizações
class CustomUserAdmin(UserAdmin):
    # Adicione aqui os campos que você quer ver na lista de usuários,
    # ou para filtrar, etc. Por enquanto, vamos manter o padrão do UserAdmin.
    # Exemplo: list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'perfil') # Se tivesse o campo 'perfil'
    pass

# Registrando os modelos para aparecerem na interface de administração
admin.site.register(Usuario, CustomUserAdmin) # Usamos nosso CustomUserAdmin
admin.site.register(CategoriaProduto)
admin.site.register(Produto)
admin.site.register(Cliente)
# admin.site.register(Venda) # Comentado por enquanto, pois o ItemVenda é melhor gerenciado inline
# admin.site.register(ItemVenda) # Geralmente não registramos ItemVenda diretamente

# Para uma melhor experiência ao gerenciar Vendas e seus Itens,
# podemos usar 'inlines'. Isso permite adicionar/editar ItemVenda
# diretamente na página de edição da Venda.

class ItemVendaInline(admin.TabularInline): # Ou admin.StackedInline para layout diferente
    model = ItemVenda
    extra = 1 # Quantos formulários de item em branco mostrar por padrão
    # readonly_fields = ('subtotal',) # Se quiser mostrar o subtotal calculado
    # Adicione campos para exibir na linha, se necessário:
    # fields = ('produto', 'quantidade', 'precoUnitarioVenda', 'subtotal') # Ajuste a ordem

class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'usuario', 'dataHoraVenda', 'valorTotalVenda', 'statusVenda', 'statusPagamento')
    list_filter = ('statusVenda', 'statusPagamento', 'dataHoraVenda', 'usuario')
    search_fields = ('id', 'cliente__nome', 'usuario__username') # Busca pelo id da venda, nome do cliente ou username do vendedor
    date_hierarchy = 'dataHoraVenda' # Adiciona navegação por datas
    inlines = [ItemVendaInline] # Adiciona os itens da venda na mesma página
    readonly_fields = ('dataHoraVenda', 'valorTotalVenda') # Campos que não devem ser editados diretamente no admin (valorTotal é calculado)

    # Se quiser calcular e salvar valorTotalVenda automaticamente no admin (embora a API já faça isso)
    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)
    #     # Recalcular valor total se itens forem modificados via admin
    #     # Esta lógica pode ser complexa no admin, idealmente a API é a fonte da verdade.

    # def save_related(self, request, form, formsets, change):
    #     super().save_related(request, form, formsets, change)
    #     # Lógica para recalcular o valorTotalVenda da Venda quando os ItemVenda são salvos
    #     venda = form.instance
    #     total = 0
    #     for item in venda.itens.all():
    #         total += item.subtotal
    #     if venda.valorTotalVenda != total:
    #         venda.valorTotalVenda = total
    #         venda.save()

admin.site.register(Venda, VendaAdmin) # Registra Venda com a configuração customizada