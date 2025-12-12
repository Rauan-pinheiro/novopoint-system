# cardapio/views.py

from rest_framework import viewsets
from .models import Categoria, Produto, ValoresDeOpcoes
from .serializers import CategoriaSerializer, ProdutoSerializer, ValoresDeOpcoesSerializer
from rest_framework.permissions import IsAuthenticated

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este endpoint permite visualizar as categorias do cardápio.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    
class ProdutoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este endpoint permite visualizar todos os produtos do cardápio.
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filterset_fields = ['categoria']
    permission_classes = [IsAuthenticated]
    
class AdicionaisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Este endpoint lista todos os valores de opções que são 'adicionais de Esfiha/Pastel'.
    """
    serializer_class = ValoresDeOpcoesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ValoresDeOpcoes.objects.filter(grupo__nome='adicionais de Esfiha/Pastel')