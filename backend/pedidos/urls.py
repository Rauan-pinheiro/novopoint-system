# pedidos/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_filters.rest_framework import DjangoFilterBackend # Certifique-se de que está importado se usá-lo na view

# Importe APENAS os nomes que existem
from .views import (
    MesaViewSet, PedidoViewSet, ItemPedidoViewSet, 
    VendasDiariasView, PedidosAbertosViewSet, DashboardDiarioView
)

router = DefaultRouter()
router.register(r'mesas', MesaViewSet)
router.register(r'pedidos', PedidoViewSet, basename='pedido') # Adicionado basename para consistência
router.register(r'itens-pedido', ItemPedidoViewSet)
router.register(r'pedidos-abertos', PedidosAbertosViewSet, basename='pedidos-abertos')

urlpatterns = [
    path('', include(router.urls)),
    path('relatorios/vendas-diarias/', VendasDiariasView.as_view(), name='vendas-diarias'),
    path('dashboard/hoje/', DashboardDiarioView.as_view(), name='dashboard-hoje'),
]