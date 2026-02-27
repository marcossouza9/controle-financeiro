from sqlalchemy import Boolean, Column, Date, Float, Integer, String

from .database import Base


class Transaction(Base):
    """Tabela principal com lançamentos financeiros."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    data = Column(Date, nullable=False, index=True)
    tipo = Column(String, nullable=False, index=True)  # entrada | saida
    categoria = Column(String, nullable=False, index=True)
    forma_pagamento = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    pago = Column(Boolean, default=False, nullable=False, index=True)
