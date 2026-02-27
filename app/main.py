from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Transaction
from .schemas import TransactionCreate, TransactionOut, TransactionUpdate

# Cria as tabelas automaticamente no startup inicial.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Controle Financeiro Pessoal")

# Disponibiliza CSS/JS e demais assets estáticos.
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home():
    """Retorna a página principal da aplicação."""
    return FileResponse("app/templates/index.html")


@app.post("/api/transactions", response_model=TransactionOut, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    transaction = Transaction(**payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.get("/api/transactions", response_model=list[TransactionOut])
def list_transactions(
    month: Optional[int] = Query(default=None, ge=1, le=12),
    year: Optional[int] = Query(default=None, ge=2000, le=2100),
    tipo: Optional[str] = Query(default=None),
    only_pending: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    if month:
        query = query.filter(extract("month", Transaction.data) == month)
    if year:
        query = query.filter(extract("year", Transaction.data) == year)
    if tipo in {"entrada", "saida"}:
        query = query.filter(Transaction.tipo == tipo)
    if only_pending:
        query = query.filter(Transaction.pago.is_(False))

    return query.order_by(Transaction.data.desc(), Transaction.id.desc()).all()


@app.patch("/api/transactions/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)
):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@app.delete("/api/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    db.delete(transaction)
    db.commit()


@app.get("/api/dashboard")
def dashboard(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    today = date.today()

    # Totais do mês selecionado.
    total_entradas_mes = (
        db.query(func.coalesce(func.sum(Transaction.valor), 0.0))
        .filter(Transaction.tipo == "entrada")
        .filter(extract("month", Transaction.data) == month)
        .filter(extract("year", Transaction.data) == year)
        .scalar()
    )
    total_saidas_mes = (
        db.query(func.coalesce(func.sum(Transaction.valor), 0.0))
        .filter(Transaction.tipo == "saida")
        .filter(extract("month", Transaction.data) == month)
        .filter(extract("year", Transaction.data) == year)
        .scalar()
    )

    # Saldo atual considera apenas movimentações já pagas/recebidas.
    entradas_pagas = (
        db.query(func.coalesce(func.sum(Transaction.valor), 0.0))
        .filter(Transaction.tipo == "entrada", Transaction.pago.is_(True))
        .scalar()
    )
    saidas_pagas = (
        db.query(func.coalesce(func.sum(Transaction.valor), 0.0))
        .filter(Transaction.tipo == "saida", Transaction.pago.is_(True))
        .scalar()
    )
    saldo_atual = float(entradas_pagas - saidas_pagas)

    contas_receber = (
        db.query(Transaction)
        .filter(Transaction.tipo == "entrada", Transaction.pago.is_(False))
        .order_by(Transaction.data.asc())
        .all()
    )
    contas_pagar = (
        db.query(Transaction)
        .filter(Transaction.tipo == "saida", Transaction.pago.is_(False))
        .order_by(Transaction.data.asc())
        .all()
    )

    total_receber_pendente = sum(item.valor for item in contas_receber)
    total_pagar_pendente = sum(item.valor for item in contas_pagar)
    saldo_futuro = saldo_atual + total_receber_pendente - total_pagar_pendente

    # Serialização simplificada para destacar vencimento no front-end.
    def serialize_pending(item: Transaction):
        return {
            "id": item.id,
            "valor": item.valor,
            "data": item.data.isoformat(),
            "categoria": item.categoria,
            "descricao": item.descricao,
            "forma_pagamento": item.forma_pagamento,
            "vencida": item.data < today,
        }

    return {
        "saldo_atual": saldo_atual,
        "total_entradas_mes": float(total_entradas_mes),
        "total_saidas_mes": float(total_saidas_mes),
        "saldo_futuro": float(saldo_futuro),
        "contas_pagar": [serialize_pending(item) for item in contas_pagar],
        "contas_receber": [serialize_pending(item) for item in contas_receber],
    }
