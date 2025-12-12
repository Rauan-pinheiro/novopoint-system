import PyInstaller.__main__
import os
import escpos

# 1. Encontra onde está o arquivo capabilities.json na sua máquina
caminho_arquivo = os.path.join(os.path.dirname(escpos.__file__), 'capabilities.json')

print(f"--- Arquivo encontrado em: {caminho_arquivo} ---")

# 2. Roda o PyInstaller com os comandos certos
# O formato do add-data no Windows é: "origem;destino"
dados_adicionais = f'{caminho_arquivo};escpos'

PyInstaller.__main__.run([
    'vigia.py',                # Seu script principal
    '--onefile',               # Criar um único arquivo .exe
    '--noconsole',             # Não mostrar a tela preta (se quiser ver erros, remova essa linha)
    '--name=VigiaDevFlow',     # Nome do executável final
    f'--add-data={dados_adicionais}', # A MÁGICA: Inclui o arquivo que estava faltando
])