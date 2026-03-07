from fastapi import APIRouter, Depends, HTTPException, status
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
    current_user: User = Depends(deps.get_current_user) # exigimos que este logueado
):
    # 1. calculo el nuevo saldo sumando lo actual con la recarga
    new_balance = current_user.wallet_balance + transaction_in.amount
    
    # 2. actualizo el saldo en la memoria del perfil del usuario
    current_user.wallet_balance = new_balance
    
    # 3. creo el recibo inmutable para el historial (auditoria)
    new_transaction = WalletTransaction(
        user_id=current_user.id, # uso el id interno (Integer) super rapido
        amount=transaction_in.amount,
        description=transaction_in.description,
        balance_after_transaction=new_balance
    )
    
    # 4. guardo ambos cambios al mismo tiempo (Atomicidad)
    db.add(new_transaction)
    db.commit() # aqui se ejecuta la escritura real en la base de datos
    db.refresh(new_transaction)
    
    return new_transaction