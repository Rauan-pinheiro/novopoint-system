# cardapio/models.py

from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    permite_adicionais = models.BooleanField(default=False, help_text="Marque se produtos desta categoria podem ter itens adicionais.")

    def __str__(self):
        return self.nome

# --- CLASSE MOVIDA PARA CIMA ---
# GrupoDeOpcoes precisa ser definido ANTES de Produto
class GrupoDeOpcoes(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Grupos de Opções"

    def __str__(self):
        return self.nome

# --- CLASSE MOVIDA PARA CIMA ---
# ValoresDeOpcoes precisa ser definido ANTES de PrecosPorOpcao
class ValoresDeOpcoes(models.Model):
    # O related_name 'valores_de_opcoes' será usado pelo serializer
    grupo = models.ForeignKey(GrupoDeOpcoes, on_delete=models.CASCADE, related_name='valores_de_opcoes')
    valor = models.CharField(max_length=100)
    preco_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor a ser somado se esta opção for escolhida (ex: adicionais).")
    
    # Campo para ajudar o serializer de impressão (opcional, mas recomendado)
    is_adicional = models.BooleanField(default=False, help_text="Marque se esta opção é um adicional (ex: Bacon Extra) e não uma opção principal (ex: Tamanho).")

    class Meta:
        verbose_name_plural = "Valores de Opções"

    def __str__(self):
        return f'{self.grupo.nome} - {self.valor}'

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    preco_fixo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Use se o preço for único.")
    
    # Agora o 'GrupoDeOpcoes' já existe e é reconhecido
    opcoes_obrigatorias = models.ManyToManyField(
        GrupoDeOpcoes,
        related_name='produtos_com_opcao_obrigatoria',
        blank=True,
        help_text="Anexe grupos de opções extras que são obrigatórias (ex: Sabor do Suco)."
    )

    def __str__(self):
        return self.nome
        
class PrecosPorOpcao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='precos_opcoes')
    valor_opcao = models.ForeignKey(ValoresDeOpcoes, on_delete=models.CASCADE, related_name='precos')
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name_plural = "Preços por Opção"
        unique_together = [['produto', 'valor_opcao']] # Garante que não haja preços duplicados

    def __str__(self):
        return f'{self.produto.nome} ({self.valor_opcao.valor}) - R$ {self.preco}'