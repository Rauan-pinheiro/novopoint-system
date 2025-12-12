# cardapio/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProdutoViewSet, AdicionaisViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'adicionais', AdicionaisViewSet, basename='adicional')

urlpatterns = [
    path('', include(router.urls)),
]