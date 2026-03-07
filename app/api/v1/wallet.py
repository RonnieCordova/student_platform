from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.wallet_transaction import TransactionCreate, TransactionOut
from app.models.user import User
from app.models.wallet_transaction import WalletTransaction

router = APIRouter()

@router.post("/deposit", response_model=TransactionOut)
def deposit_funds(
    transaction_in: TransactionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Endpoint para recargar saldo en la billetera virtual.
    """
    # 1. validamos que el monto sea logico (no recargas negativas)
    if transaction_in.amount <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
    
    # 2. calculamos el nuevo saldo
    new_balance = current_user.wallet_balance + transaction_in.amount
    
    # 3. actualizamos el saldo del usuario
    current_user.wallet_balance = new_balance
    
    # 4. creamos el registro inmutable de la transaccion (auditoria)
    new_transaction = WalletTransaction(
        user_id=current_user.id, # usamos el id interno de forma segura
        amount=transaction_in.amount,
        description=transaction_in.description,
        balance_after_transaction=new_balance
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return new_transaction