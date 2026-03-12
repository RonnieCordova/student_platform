from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import SessionLocal
from app.models import resource as resource_model
from app.schemas import resource as resource_schema
from app.models import user as user_model
from app.models import subject as subject_model
from app.models import wallet_transaction as wallet_transaction_model
from app.api.deps import get_current_user

router = APIRouter()

PLATFORM_FEE_PERCENTAGE = 0.15 # 15% de comision en recursos premium

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST: Subir un nuevo recurso (Solo para usuarios autenticados)
@router.post("/", response_model=resource_schema.ResourceResponse, status_code=status.HTTP_201_CREATED)
def upload_resource(
    resource_in: resource_schema.ResourceCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # 1. verifico si la materia existe
    subject = db.query(subject_model.Subject).filter(subject_model.Subject.id == resource_in.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="La materia especificada no existe")

    # 2. validacion de negocio: si es premium, el precio debe ser mayor a 0
    if resource_in.is_premium and resource_in.price <= 0:
        raise HTTPException(status_code=400, detail="Un recurso premium debe tener un precio mayor a $0.00")

    # 3. creo el recurso vinculandolo al usuario que lo sube
    new_resource = resource_model.Resource(
        title=resource_in.title,
        description=resource_in.description,
        file_url=resource_in.file_url,
        is_premium=resource_in.is_premium,
        price=resource_in.price,
        subject_id=resource_in.subject_id,
        owner_id=current_user.id
    )
    
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

# GET: Listar todos los recursos disponibles (con filtro opcional por materia)
@router.get("/", response_model=List[resource_schema.ResourceResponse])
def get_resources(
    subject_id: int = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user) # requiero login para ver la boveda
):
    query = db.query(resource_model.Resource)
    
    if subject_id:
        query = query.filter(resource_model.Resource.subject_id == subject_id)
        
    resources = query.offset(skip).limit(limit).all()
    return resources

# POST: Comprar o descargar un recurso
@router.post("/{public_id}/download", status_code=status.HTTP_200_OK)
def download_resource(
    public_id: UUID,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # 1. busco el recurso por su ID publico seguro
    resource = db.query(resource_model.Resource).filter(resource_model.Resource.public_id == public_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")

    # 2. si el recurso es del mismo usuario que lo creo, lo descarga gratis
    if resource.owner_id == current_user.id:
        return {"message": "Descarga exitosa (Propietario)", "file_url": resource.file_url}

    # 3. LOGICA TRANSACCIONAL: Si es premium, cobramos
    if resource.is_premium:
        if current_user.wallet_balance < resource.price:
            raise HTTPException(
                status_code=400, 
                detail=f"Saldo insuficiente. El recurso cuesta ${resource.price}"
            )

        # --- UPDATE ATÓMICO (Blindaje contra sesiones cruzadas) ---
        
        # A) Cobro al comprador
        db.query(user_model.User).filter(user_model.User.id == current_user.id).update(
            {"wallet_balance": user_model.User.wallet_balance - resource.price}
        )
        
        purchase_tx = wallet_transaction_model.WalletTransaction(
            user_id=current_user.id,
            amount=-resource.price,
            description=f"Compra de recurso premium: {resource.title}",
            balance_after_transaction=current_user.wallet_balance - resource.price
        )
        db.add(purchase_tx)

        # B) Pago al creador del recurso (aplicando la comision de la plataforma)
        creator_payment = resource.price * (1 - PLATFORM_FEE_PERCENTAGE)
        
        # busco al dueño actual para saber su saldo antes de sumarle
        owner = db.query(user_model.User).filter(user_model.User.id == resource.owner_id).first()
        
        db.query(user_model.User).filter(user_model.User.id == resource.owner_id).update(
            {"wallet_balance": user_model.User.wallet_balance + creator_payment}
        )
        
        sale_tx = wallet_transaction_model.WalletTransaction(
            user_id=resource.owner_id,
            amount=creator_payment,
            description=f"Venta de recurso: {resource.title} (Comisión {PLATFORM_FEE_PERCENTAGE*100}% descontada)",
            balance_after_transaction=owner.wallet_balance + creator_payment
        )
        db.add(sale_tx)

    # 4. incremento las metricas de descarga del archivo
    db.query(resource_model.Resource).filter(resource_model.Resource.id == resource.id).update(
        {"downloads": resource_model.Resource.downloads + 1}
    )
    
    db.commit()

    return {
        "message": "Descarga exitosa", 
        "file_url": resource.file_url,
        "note": "En produccion, esta URL seria un enlace temporal firmado de AWS S3"
    }