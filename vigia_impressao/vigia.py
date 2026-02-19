
import requests
import time
from escpos.printer import Win32Raw 
import schedule
from datetime import datetime
import traceback
from decouple import config

# DADOS DA EMPRESA
NOME_EMPRESA = config('NOME_EMPRESA')
ENDERECO_1 = config('ENDERECO_1')
CONTATO = config('CONTATO')
MSG_RODAPE = "Obrigado pela preferencia!\nVolte Sempre!"

# CONFIGURAÇÕES
API_BASE_URL = config('API_BASE_URL') 
LOGIN_URL = f"{API_BASE_URL}/token/"
PEDIDOS_URL = f"{API_BASE_URL}/pedidos/"
DETALHES_PEDIDO_URL_BASE = f"{API_BASE_URL}/pedidos/"

API_USERNAME = config('API_USERNAME')
API_PASSWORD = config('senha_impressora')

# NOME DA IMPRESSORA NO WINDOWS
PRINTER_NAME = config('PRINTER_NAME')

INTERVALO_VERIFICACAO_SEGUNDOS = config('INTERVALO_VERIFICACAO_SEGUNDOS', cast=int)

ENCODING = 'cp850'
auth_token = None

# FUNÇÕES DE CONEXÃO
def fazer_login():
    global auth_token
    print(f"[{datetime.now()}] Conectando...")
    try:
        r = requests.post(LOGIN_URL, data={'username': API_USERNAME, 'password': API_PASSWORD})
        r.raise_for_status()
        auth_token = r.json().get('access')
        if auth_token: print("Login OK!"); return True
    except: return False
    return False

def get_headers():
    if not auth_token: return None
    return {'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}

def buscar_pedidos_pendentes():
    headers = get_headers()
    if not headers: 
        if not fazer_login(): return []
        headers = get_headers()
    
    lista = []
    for st in ['em_preparo', 'solicitado_conta']:
        try:
            r = requests.get(PEDIDOS_URL, headers=headers, params={'status': st})
            if r.status_code == 200: lista.extend(r.json())
            elif r.status_code == 401: fazer_login()
        except: pass
    return lista

def buscar_detalhes(pid):
    try:
        return requests.get(f"{DETALHES_PEDIDO_URL_BASE}{pid}/para-impressao/", headers=get_headers()).json()
    except: return None

def atualizar_status(pid, status):
    try: requests.patch(f"{PEDIDOS_URL}{pid}/", headers=get_headers(), json={'status': status}); return True
    except: return False

def imprimir_cupom(pedido, tipo):
    try:
        p = Win32Raw(printer_name=PRINTER_NAME)
        p.codepage = ENCODING
        
        # CABEÇALHO (Identidade Visual)
        p.set(align='center')
        
        p.set(width=2, height=2, bold=True)
        p.text(f"{NOME_EMPRESA}\n")
        
        # Endereço e Contato Normal
        p.set(width=1, height=1, bold=False)
        if ENDERECO_1: p.text(f"{ENDERECO_1}\n")
        if CONTATO: p.text(f"{CONTATO}\n")
        
        p.text("-" * 32 + "\n")

        # METADADOS
        if tipo == 'CONTA':
            p.set(bold=True); p.text("EXTRATO DE CONFERENCIA\n"); p.set(bold=False)
        else:
            p.set(bold=True, width=2, height=2); p.text("COZINHA\n"); p.set(width=1, height=1, bold=False)

        p.set(align='left')
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
        p.text(f"DATA: {data_hora}\n")
        p.text(f"PEDIDO: #{pedido.get('id')}   Mesa: {pedido.get('mesa', 'Balcao')}\n")
        if pedido.get('garcom'): p.text(f"ATENDENTE: {pedido['garcom']}\n")
        if pedido.get('nome_cliente'): p.text(f"CLIENTE: {pedido['nome_cliente']}\n")
        
        p.text("-" * 32 + "\n")

        # ITENS
        if tipo == 'CONTA':
            p.set(bold=True)
            p.text(f"{'ITEM':<20} {'V.UNIT':>10}\n")
            p.set(bold=False)
        
        total_conta = 0.0
        itens = pedido.get('itens', [])
        
        for item in itens:
            qtd = item.get('quantidade', 1)
            nome = item.get('produto', 'Item')
            opcoes = item.get('opcoes_nomes', [])
            adds = item.get('adicionais_nomes', [])
            obs = item.get('observacoes', '')
            preco_total_item = float(item.get('preco_final', 0))
            total_conta += preco_total_item
            
            nome_full = f"{qtd}x {nome}"
            if opcoes: nome_full += f" ({','.join(opcoes)})"

            if tipo == 'COZINHA':
                p.set(width=2, height=2, bold=True)
                p.text(f"{nome_full}\n")
                p.set(width=1, height=1, bold=False)
            else:
                p.set(bold=True)
                p.text(f"{nome_full}")
                p.set(align='right')
                p.text(f" R$ {preco_total_item:.2f}\n")
                p.set(align='left', bold=False)

            if adds: p.text(f"  + {', '.join(adds)}\n")
            if obs: p.text(f"  Obs: {obs}\n")
            
            if tipo == 'COZINHA': p.text("\n")

        p.text("-" * 32 + "\n")

        # TOTAL E RODAPÉ (Só na Conta)
        if tipo == 'CONTA':
            p.set(align='right', width=2, height=2, bold=True)
            p.text(f"TOTAL: R$ {total_conta:.2f}\n")
            
            p.set(width=1, height=1, bold=False, align='center')
            p.text("-" * 32 + "\n")
            p.text(f"{MSG_RODAPE}\n")
            p.text("--------------------------------\n")
            p.text("Nao vale como documento fiscal\n")

        p.text("\n\n")
        p.cut()
        p.close()
        return True

    except Exception as e:
        print(f"Erro Print: {e}")
        return False

# LOOP 
def ciclo():
    pedidos = buscar_pedidos_pendentes()
    for p in pedidos:
        pid = p['id']
        status = p['status']
        d = buscar_detalhes(pid)
        if not d: continue

        ok = False
        novo_st = ''
        
        if status == 'em_preparo':
            print(f"-> Cozinha #{pid}")
            if imprimir_cupom(d, 'COZINHA'): ok=True; novo_st='entregue'
        elif status == 'solicitado_conta':
            print(f"-> Conta #{pid}")
            if imprimir_cupom(d, 'CONTA'): ok=True; novo_st='conta_impressa'
            
        if ok: atualizar_status(pid, novo_st); time.sleep(2)

if __name__ == "__main__":
    print("--- VIGIA PREMIUM (WINDOWS DRIVER) ---")
    fazer_login()
    schedule.every(3).seconds.do(ciclo)
    while True:
        try: schedule.run_pending(); time.sleep(1)
        except KeyboardInterrupt: break
        except Exception: time.sleep(5)