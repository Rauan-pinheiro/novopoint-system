# pedidos/models.py

from django.db import models
from cardapio.models import Produto, ValoresDeOpcoes
from django.contrib.auth.models import User

# Representa as mesas do estabelecimento
class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f'Mesa {self.numero}'

# Representa o pedido completo de uma mesa
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('anotado', 'Anotado'),
        ('em_preparo', 'Em Preparo'),
        ('entregue', 'Entregue'),
        ('solicitado_conta', 'Solicitado Conta'), 
        ('conta_impressa', 'Conta Impressa'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, related_name='pedidos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='anotado')
    data_hora = models.DateTimeField(auto_now_add=True)
    garcom = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nome_cliente = models.CharField(max_length=100, blank=True, null=True, help_text="Nome de referência para o pedido, ex: Mesa do Renato")

    def __str__(self):
        # Usa self.mesa.numero se a mesa existir, senão mostra 'N/A'
        nome_mesa = self.mesa.numero if self.mesa else 'N/A'
        return f'Pedido da Mesa {nome_mesa} - {self.data_hora.strftime("%d/%m/%Y %H:%M")}'

# Representa um item específico dentro de um Pedido
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    opcoes_selecionadas = models.ManyToManyField(ValoresDeOpcoes, blank=True)
    observacoes = models.TextField(blank=True, null=True, help_text="Ex: sem cebola, ponto da carne, etc.")
    preco_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} para o {self.pedido}'