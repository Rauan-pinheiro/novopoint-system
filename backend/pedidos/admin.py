
from django.contrib import admin
from .models import Mesa, Pedido, ItemPedido

# Classe para mostrar os Itens do Pedido diretamente na tela do Pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1  # Quantos campos extras de item de pedido mostrar
    
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'mesa', 'status', 'data_hora')
    list_filter = ('status', 'mesa')
    inlines = [ItemPedidoInline]

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'disponivel')
    list_filter = ('disponivel',)

# O ItemPedido será gerenciado através do PedidoAdmin, então não precisa de um registro separado
# admin.site.register(ItemPedido)