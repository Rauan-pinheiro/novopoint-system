# pedidos/serializers.py

from rest_framework import serializers
from .models import Mesa, Pedido, ItemPedido # Importa os modelos locais
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        return data

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id', 'numero', 'disponivel']

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'mesa', 'status', 'data_hora', 'garcom', 'nome_cliente']
        read_only_fields = ['data_hora', 'garcom']

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ['id', 'pedido', 'produto', 'quantidade', 'opcoes_selecionadas', 'observacoes']

# --- CÓDIGO MOVIDO PARA O LUGAR CORRETO ---

class ItemPedidoImpressaoSerializer(serializers.ModelSerializer):
    """
    Serializer para formatar os itens do pedido para a impressão,
    separando opções de adicionais.
    """
    produto = serializers.StringRelatedField()
    opcoes_nomes = serializers.SerializerMethodField()
    adicionais_nomes = serializers.SerializerMethodField()

    class Meta:
        model = ItemPedido
        fields = ['quantidade', 'produto', 'observacoes', 'opcoes_nomes', 'adicionais_nomes', 'preco_final']

    def get_opcoes_nomes(self, obj):
        """Retorna nomes de opções que NÃO são adicionais (baseado no campo 'is_adicional')"""
        return list(obj.opcoes_selecionadas.filter(is_adicional=False).values_list('valor', flat=True))

    def get_adicionais_nomes(self, obj):
        """Retorna nomes de opções que SÃO adicionais"""
        return list(obj.opcoes_selecionadas.filter(is_adicional=True).values_list('valor', flat=True))


class PedidoImpressaoSerializer(serializers.ModelSerializer):
    """
    Serializer principal para a impressão, que aninha os itens já formatados.
    """
    mesa = serializers.StringRelatedField()
    garcom = serializers.StringRelatedField()
    itens = ItemPedidoImpressaoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'mesa', 'nome_cliente', 'garcom', 'data_hora', 'itens']

# --- FIM DO CÓDIGO MOVIDO ---

class ItemPedidoParaCaixaSerializer(serializers.ModelSerializer):
    produto = serializers.StringRelatedField()
    class Meta:
        model = ItemPedido
        fields = ['quantidade', 'produto', 'preco_final']

class PedidoParaCaixaSerializer(serializers.ModelSerializer):
    itens = ItemPedidoParaCaixaSerializer(many=True, read_only=True)
    mesa = serializers.StringRelatedField()
    garcom = serializers.StringRelatedField()
    class Meta:
        model = Pedido
        fields = ['id', 'mesa', 'nome_cliente', 'garcom', 'itens']

class ItemPedidoDetalhadoSerializer(serializers.ModelSerializer):
    produto = serializers.StringRelatedField()
    class Meta:
        model = ItemPedido
        fields = ['quantidade', 'produto', 'observacoes', 'preco_final']

class PedidoDashboardSerializer(serializers.ModelSerializer):
    itens = ItemPedidoDetalhadoSerializer(many=True, read_only=True)
    mesa = serializers.StringRelatedField()
    garcom = serializers.StringRelatedField()
    total_pedido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Pedido
        fields = ['id', 'mesa', 'nome_cliente', 'garcom', 'status', 'data_hora', 'itens', 'total_pedido']