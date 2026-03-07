from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import resource as resource_model
from app.models import user as user_model
from app.models import wallet_transaction as wallet_transaction_model
from app.schemas import resource as resource_schema
from app.api.deps import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=resource_schema.ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    payload: resource_schema.ResourceCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # verifico que el tipo de archivo sea permitido
    normalized_file_type = payload.file_type.strip().lower()
    if normalized_file_type not in {"pdf", "doc", "docx"}:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    # guardo el recurso con owner automatico
    new_resource = resource_model.Resource(
        owner_id=current_user.id,
        title=payload.title,
        subject=payload.subject,
        file_type=payload.file_type,
        file_url=payload.file_url,
        is_premium=payload.is_premium,
        is_approved=False,
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource


@router.get("/", response_model=List[resource_schema.ResourceResponse])
def list_resources(
    subject: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    # construyo la consulta de recursos aprobados
    query = db.query(resource_model.Resource).filter(resource_model.Resource.is_approved.is_(True))
    if subject:
        query = query.filter(resource_model.Resource.subject == subject)

    return query.offset(skip).limit(limit).all()


@router.post("/{resource_id}/download", response_model=resource_schema.ResourceDownloadResponse)
def download_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # busco el recurso aprobado
    resource = db.query(resource_model.Resource).filter(
        resource_model.Resource.id == resource_id,
        resource_model.Resource.is_approved.is_(True),
    ).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")

    # cobro solo si el recurso es premium
    if resource.is_premium:
        # verifico si tiene saldo disponible
        if float(current_user.wallet_balance) < 1.0:
            raise HTTPException(status_code=400, detail="Fondos insuficientes para descargar este recurso")

        owner = db.query(user_model.User).filter(user_model.User.id == resource.owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Propietario del recurso no encontrado")

        # descuento al estudiante
        current_user.wallet_balance = float(current_user.wallet_balance) - 1.0

        # acredito al creador del recurso
        owner.wallet_balance = float(owner.wallet_balance) + 0.80

        # guardo transaccion del comprador
        buyer_tx = wallet_transaction_model.WalletTransaction(
            user_id=current_user.id,
            amount=-1.0,
            transaction_type="resource_download_debit",
            description=f"Descarga premium del recurso #{resource.id}",
        )
        db.add(buyer_tx)

        # guardo transaccion del creador
        owner_tx = wallet_transaction_model.WalletTransaction(
            user_id=owner.id,
            amount=0.80,
            transaction_type="resource_download_credit",
            description=f"Ganancia por descarga del recurso #{resource.id}",
        )
        db.add(owner_tx)

    # incremento contador de descargas
    resource.downloads = int(resource.downloads) + 1
    db.commit()
    db.refresh(resource)

    return {
        "file_url": resource.file_url,
        "downloads": resource.downloads,
    }
