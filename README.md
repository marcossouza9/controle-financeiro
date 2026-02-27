# Controle Financeiro Pessoal

Aplicação web para gestão financeira com **FastAPI + SQLite + HTML/CSS/JS**, pronta para execução local.

## Funcionalidades

- Cadastro de **entradas e saídas** com:
  - valor
  - data
  - tipo
  - categoria
  - forma de pagamento
  - descrição opcional
  - status pago/recebido
- Dashboard com:
  - saldo atual
  - total de entradas do mês
  - total de saídas do mês
  - previsão de saldo futuro
- Listas de:
  - contas a pagar
  - contas a receber
- Indicação visual de contas vencidas
- Filtro por mês e ano
- Listagem completa de lançamentos com ações para marcar pago/pendente e excluir

## Estrutura de pastas

```text
controle-financeiro/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── static/
│   │   ├── css/styles.css
│   │   └── js/app.js
│   └── templates/index.html
├── requirements.txt
└── README.md
```

## Como rodar

### 1) Criar e ativar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Iniciar aplicação

```bash
uvicorn app.main:app --reload
```

### 4) Acessar no navegador

- Interface web: http://127.0.0.1:8000
- Documentação da API: http://127.0.0.1:8000/docs

## Banco de dados

- O arquivo SQLite `financeiro.db` é criado automaticamente na primeira execução.
- A tabela `transactions` é criada no startup da aplicação.

## Observações

- O saldo atual considera lançamentos marcados como **Pago/Recebido**.
- A previsão de saldo futuro considera todas as contas pendentes (a pagar e a receber).
