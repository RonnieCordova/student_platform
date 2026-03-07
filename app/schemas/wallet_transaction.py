from pydantic import BaseModel, UUID4
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    description: str

# cuando el usuario quiere recargar saldo desde React
class TransactionCreate(TransactionBase):
    pass # por ahora solo necesitamos el monto y la descripcion

# lo que le mandamos a React para pintar el historial de movimientos
class TransactionOut(TransactionBase):
    id: UUID4
    balance_after_transaction: float
    created_at: datetime

    class Config:
        from_attributes = True