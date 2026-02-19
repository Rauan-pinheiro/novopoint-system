# pedidos/views.py

from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, time 
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action 
from django_filters.rest_framework import DjangoFilterBackend

from .models import Mesa, Pedido, ItemPedido
from cardapio.models import Produto, PrecosPorOpcao, ValoresDeOpcoes

from .serializers import (
    MesaSerializer, PedidoSerializer, ItemPedidoSerializer, MyTokenObtainPairSerializer,
    PedidoParaCaixaSerializer, PedidoDashboardSerializer, PedidoImpressaoSerializer 
)

# FUNÇÃO AUXILIAR DE DATA
def get_intervalo_dia_trabalho():
    agora_local = timezone.localtime(timezone.now())
    hora_fechamento = time(2, 0, 0) # 2:00H
    if agora_local.time() < hora_fechamento:
        data_hoje = agora_local.date() - timezone.timedelta(days=1)
    else:
        data_hoje = agora_local.date()
    inicio_dia = timezone.make_aware(datetime.combine(data_hoje, hora_fechamento))
    fim_dia = inicio_dia + timezone.timedelta(days=1)
    return inicio_dia, fim_dia

# VIEWS DE AUTENTICAÇÃO
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# VIEWS DO APP PEDIDOS
class MesaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [IsAuthenticated]

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-data_hora')
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def perform_create(self, serializer):
        serializer.save(garcom=self.request.user)

    # AÇÃO DE IMPRESSÃO
    @action(detail=True, methods=['get'], url_path='para-impressao', permission_classes=[IsAuthenticated])
    def para_impressao(self, request, pk=None):
        pedido = self.get_object()
        serializer = PedidoImpressaoSerializer(pedido)
        return Response(serializer.data)

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        # código de cálculo de preço
        produto_id = self.request.data.get('produto')
        opcoes_ids = self.request.data.get('opcoes_selecionadas', [])
        quantidade = int(self.request.data.get('quantidade', 1))
        produto = Produto.objects.get(id=produto_id)
        preco_base = 0
        if produto.preco_fixo:
            preco_base = produto.preco_fixo
        elif opcoes_ids:
            try:
                preco_opcao_obj = PrecosPorOpcao.objects.get(produto=produto, valor_opcao_id=opcoes_ids[0])
                preco_base = preco_opcao_obj.preco
            except PrecosPorOpcao.DoesNotExist:
                preco_base = 0
        preco_adicionais = 0
        opcoes_selecionadas_objs = ValoresDeOpcoes.objects.filter(id__in=opcoes_ids)
        for opcao in opcoes_selecionadas_objs:
            preco_adicionais += opcao.preco_adicional
        preco_unitario = preco_base + preco_adicionais
        preco_final_item = preco_unitario * quantidade
        serializer.save(preco_final=preco_final_item)

class PedidosAbertosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PedidoParaCaixaSerializer
    permission_classes = [IsAuthenticated, IsAdminUser] # Garante segurança dupla

    def get_queryset(self):
        inicio_dia, fim_dia = get_intervalo_dia_trabalho()
        # Lista exata dos status que considera "Em Aberto" (já saíram do 'anotado')
        status_validos = ['em_preparo', 'entregue', 'solicitado_conta', 'conta_impressa']
        
        return Pedido.objects.filter(
            data_hora__gte=inicio_dia,
            data_hora__lt=fim_dia,
            status__in=status_validos
        ).order_by('data_hora')

# VIEWS DE RELATÓRIO / DASHBOARD
class VendasDiariasView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, format=None):
        inicio_dia, fim_dia = get_intervalo_dia_trabalho()
        total_apurado = ItemPedido.objects.filter(
            pedido__status='pago',
            pedido__data_hora__gte=inicio_dia,
            pedido__data_hora__lt=fim_dia
        ).aggregate(total=Sum('preco_final'))['total'] or 0
        return Response({'total_apurado_hoje': total_apurado})

class DashboardDiarioView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, format=None):
        agora_local = timezone.localtime(timezone.now())
        inicio_dia, fim_dia = get_intervalo_dia_trabalho()
        
        total_apurado_dia = ItemPedido.objects.filter(
            pedido__status='pago',
            pedido__data_hora__gte=inicio_dia,
            pedido__data_hora__lt=fim_dia
        ).aggregate(total=Sum('preco_final'))['total'] or 0

        # Pega o primeiro dia do mês atual
        inicio_mes = agora_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total_apurado_mes = ItemPedido.objects.filter(
            pedido__status='pago',
            pedido__data_hora__gte=inicio_mes
        ).aggregate(total=Sum('preco_final'))['total'] or 0
        
        # Pega o primeiro dia do ano atual
        inicio_ano = agora_local.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        total_apurado_ano = ItemPedido.objects.filter(
            pedido__status='pago',
            pedido__data_hora__gte=inicio_ano
        ).aggregate(total=Sum('preco_final'))['total'] or 0
        
        base_queryset = Pedido.objects.filter(
            data_hora__gte=inicio_dia,
            data_hora__lt=fim_dia
        ).annotate(
            total_pedido=Sum('itens__preco_final')
        ).order_by('-data_hora')
        pedidos_pagos = base_queryset.filter(status='pago')
        pedidos_em_aberto = base_queryset.filter(
            status__in=['em_preparo', 'entregue', 'solicitado_conta', 'conta_impressa']
        )
        pedidos_cancelados = base_queryset.filter(status='cancelado')
        pagos_serializer = PedidoDashboardSerializer(pedidos_pagos, many=True)
        abertos_serializer = PedidoDashboardSerializer(pedidos_em_aberto, many=True)
        cancelados_serializer = PedidoDashboardSerializer(pedidos_cancelados, many=True)
        data = {
            'total_apurado_hoje': total_apurado_dia,
            'total_apurado_mes': total_apurado_mes,
            'total_apurado_ano': total_apurado_ano,
            'pedidos_pagos': pagos_serializer.data,
            'pedidos_em_aberto': abertos_serializer.data,
            'pedidos_cancelados': cancelados_serializer.data,
        }
        return Response(data)