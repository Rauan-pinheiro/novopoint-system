
from rest_framework import serializers
from .models import Categoria, Produto, GrupoDeOpcoes, ValoresDeOpcoes, PrecosPorOpcao

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'permite_adicionais']

# Um serializer simples para os valores (ex: "Açaí")
class ValoresDeOpcoesSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValoresDeOpcoes
        fields = ['id', 'valor']

# Um serializer para o grupo (ex: "Sabor do Suco") que mostra seus valores
class GrupoDeOpcoesDetalhadoSerializer(serializers.ModelSerializer):
    # Usa o related_name 'valores_de_opcoes' que definimos no models.py
    valores = ValoresDeOpcoesSimplesSerializer(many=True, read_only=True, source='valores_de_opcoes') 

    class Meta:
        model = GrupoDeOpcoes
        fields = ['id', 'nome', 'valores']

class ValoresDeOpcoesSerializer(serializers.ModelSerializer):
    # Adiciona o grupo para saber o nome (ex: "Tipo de Esfiha")
    grupo_nome = serializers.StringRelatedField(source='grupo.nome', read_only=True)
    
    class Meta:
        model = ValoresDeOpcoes
        # Adicionado 'is_adicional' e 'grupo_nome'
        fields = ['id', 'valor', 'preco_adicional', 'is_adicional', 'grupo_nome']

class PrecosPorOpcaoSerializer(serializers.ModelSerializer):
    # Modificado para ValoresDeOpcoesSerializer para enviar 'is_adicional' e 'grupo_nome'
    valor_opcao = ValoresDeOpcoesSerializer(read_only=True)

    class Meta:
        model = PrecosPorOpcao
        fields = ['preco', 'valor_opcao']

class ProdutoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    precos_opcoes = PrecosPorOpcaoSerializer(many=True, read_only=True)
    
    opcoes_obrigatorias = GrupoDeOpcoesDetalhadoSerializer(many=True, read_only=True)

    class Meta:
        model = Produto
        # 'opcoes_obrigatorias' ADICIONADO AO FIELDS
        fields = ['id', 'nome', 'descricao', 'categoria', 'preco_fixo', 'precos_opcoes', 'opcoes_obrigatorias']