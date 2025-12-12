# cardapio/admin.py

from django.contrib import admin
from .models import Categoria, Produto, GrupoDeOpcoes, ValoresDeOpcoes, PrecosPorOpcao

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'permite_adicionais')

@admin.register(ValoresDeOpcoes)
class ValoresDeOpcoesAdmin(admin.ModelAdmin):
    # Mostra o grupo e se é um adicional na lista
    list_display = ('valor', 'grupo', 'preco_adicional', 'is_adicional')
    list_filter = ('grupo', 'is_adicional') # Permite filtrar por grupo

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco_fixo')
    list_filter = ('categoria',)
    # Permite editar o ManyToManyField 'opcoes_obrigatorias' facilmente
    filter_horizontal = ('opcoes_obrigatorias',)

# Registra os modelos restantes
admin.site.register(GrupoDeOpcoes)
admin.site.register(PrecosPorOpcao)