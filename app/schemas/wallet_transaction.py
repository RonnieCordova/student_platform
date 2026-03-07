from pydantic import BaseModel, UUID4, Field
from datetime import datetime

# lo que le pido a react cuando el usuario recarga saldo
class TransactionCreate(BaseModel):
    # obligo a que el monto sea mayor a 0 (gt=0)
    amount: float = Field(..., gt=0)
    description: str

# lo que le devuelvo a react para mostrar en su historial de pagos
class TransactionOut(BaseModel):
    id: UUID4
    amount: float
    description: str
    balance_after_transaction: float
    created_at: datetime
    
    class Config:
        # le digo a pydantic que traduzca los datos desde sqlalchemy sin errores
        from_attributes = True