from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


TipoLancamento = Literal["entrada", "saida"]
FormaPagamento = Literal["pix", "cartao_credito", "debito", "dinheiro"]


class TransactionBase(BaseModel):
    valor: float = Field(gt=0)
    data: date
    tipo: TipoLancamento
    categoria: str = Field(min_length=2, max_length=50)
    forma_pagamento: FormaPagamento
    descricao: Optional[str] = Field(default=None, max_length=255)
    pago: bool = False


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    valor: Optional[float] = Field(default=None, gt=0)
    data: Optional[date] = None
    tipo: Optional[TipoLancamento] = None
    categoria: Optional[str] = Field(default=None, min_length=2, max_length=50)
    forma_pagamento: Optional[FormaPagamento] = None
    descricao: Optional[str] = Field(default=None, max_length=255)
    pago: Optional[bool] = None


class TransactionOut(TransactionBase):
    id: int

    class Config:
        from_attributes = True
