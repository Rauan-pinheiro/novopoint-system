# 🍔 Novopoint — Comanda Eletrônica para Lanchonete

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Django REST](https://img.shields.io/badge/Django%20REST%20Framework-092E20?style=flat&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React%2018-20232A?style=flat&logo=react&logoColor=61DAFB)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)

Sistema full-stack feito do zero para uma **lanchonete real**. Os garçons anotam os pedidos das mesas pelo celular e a comanda **sai sozinha na impressora da cozinha**, sem ninguém precisar redigitar nada.

<!-- Adicione aqui um GIF do fluxo: ![Demo](docs/demo.gif) -->

## 🔄 Como funciona

```
 Garçom (celular)          API Django REST              Vigia de impressão (PC da loja)
┌──────────────┐  JWT   ┌──────────────────┐  polling  ┌────────────────────────────┐
│ React        │──────▶ │ /api/pedidos/    │ ◀──────── │ busca pedidos pendentes    │
│ mesas →      │        │ /api/produtos/   │           │ imprime a comanda (ESC/POS)│
│ cardápio →   │        │ /api/dashboard/  │ ◀──────── │ atualiza o status (PATCH)  │
│ pedido       │        └────────┬─────────┘           └─────────────┬──────────────┘
└──────────────┘                 │ MySQL                             ▼
                                                            🖨️ impressora térmica
```

O pedido passa pelos status **anotado → em preparo → entregue → conta solicitada → conta impressa → pago**. O vigia de impressão consulta a API periodicamente, imprime a comanda da cozinha ou a conta da mesa e avança o status, para que nada seja impresso duas vezes.

## ✨ Funcionalidades

- **App do garçom (mobile-first)**: login, mapa de mesas, cardápio por categoria e montagem do pedido com observações (ex.: "sem cebola")
- **Cardápio flexível**: produtos com preço fixo ou preço por opção (ex.: tamanho P/M/G), grupos de opções obrigatórias e adicionais pagos
- **Impressão automática** de comandas e contas em impressora térmica, por um script Python independente
- **Dashboard do dia** com faturamento e relatório de vendas diárias, considerando o "dia de trabalho" da lanchonete, que vai até as 2h da manhã
- **Autenticação JWT** com renovação automática do token no front-end (interceptor do Axios)
- **Django Admin** para gerenciar cardápio, mesas e usuários

## 🛠️ Stack

| Parte | Tecnologias |
| :--- | :--- |
| API | Python, Django 5, Django REST Framework, SimpleJWT, django-filter, django-cors-headers |
| Banco | MySQL |
| Front-end | React 18, Axios, React-Toastify |
| Impressão | Python, python-escpos, schedule, requests |
| Configuração | python-decouple (variáveis de ambiente) |

## 🚀 Como rodar localmente

**Back-end**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
# crie um arquivo .env com SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST e DB_PORT
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Front-end**
```bash
cd frontend
npm install
npm start
```

**Vigia de impressão** (Windows, com a impressora instalada)
```bash
cd vigia_impressao
pip install requests python-escpos schedule python-decouple pywin32
# .env: API_BASE_URL, API_USERNAME, senha_impressora, PRINTER_NAME, INTERVALO_VERIFICACAO_SEGUNDOS, dados da empresa
python vigia.py
```

## 📁 Estrutura

```
backend/
├── cardapio/        # categorias, produtos, opções e adicionais
├── pedidos/         # mesas, pedidos, itens, dashboard e relatórios
└── config/          # settings e rotas (JWT em /api/token/)
frontend/src/        # App.js (mesas, cardápio, pedido) e Dashboard.js
vigia_impressao/     # script que imprime as comandas na cozinha
```

## 📚 O que aprendi

- Separar o sistema em API e cliente e autenticar com JWT, incluindo o refresh token
- Modelar um cardápio real, com preço variável por opção e adicionais
- Integrar software com hardware (impressora térmica ESC/POS) em produção
- Lidar com regras do negócio, como o dia de trabalho que termina depois da meia-noite

## 👨‍💻 Autor

**Rauan Pinheiro Lima**
[LinkedIn](https://linkedin.com/in/rauanpinheiro-dev) · [GitHub](https://github.com/Rauan-pinheiro)
