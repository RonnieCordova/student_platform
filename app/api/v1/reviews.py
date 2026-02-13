from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import review as review_model
from app.schemas import review as review_schema
from app.models import user as user_model
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST: Crear una reseña
@router.post("/", response_model=review_schema.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: review_schema.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # 1. Validar que no se califique a si mismo
    if review.tutor_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes calificarte a ti mismo")

    # 2. Validar rango de estrellas (1 al 5)
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="La calificacion debe ser entre 1 y 5")

    # 3. Guardar la reseña
    new_review = review_model.Review(
        student_id=current_user.id,
        tutor_id=review.tutor_id,
        rating=review.rating,
        comment=review.comment
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # 4. Construir respuesta con nombres
    tutor_user = db.query(user_model.User).filter(user_model.User.id == review.tutor_id).first()
    
    return {
        "id": new_review.id,
        "student_id": new_review.student_id,
        "tutor_id": new_review.tutor_id,
        "rating": new_review.rating,
        "comment": new_review.comment,
        "created_at": new_review.created_at,
        "student_name": current_user.full_name or current_user.email,
        "tutor_name": tutor_user.full_name or tutor_user.email
    }

# GET: Listar reseñas (Publico)
@router.get("/", response_model=List[review_schema.ReviewResponse])
def read_reviews(
    tutor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de reseñas. 
    Puede filtrarse por ?tutor_id=X para ver opiniones de un profesor especifico.
    """
    query = db.query(review_model.Review)
    
    # Aplicar filtro si se provee un tutor_id
    if tutor_id:
        query = query.filter(review_model.Review.tutor_id == tutor_id)
        
    reviews = query.offset(skip).limit(limit).all()
    
    # Mapeo manual para incluir los nombres en la respuesta
    results = []
    for review in reviews:
        # Resolucion segura de nombres (fallback a email si no hay nombre)
        s_name = review.student.full_name if review.student and review.student.full_name else "Usuario Anónimo"
        if review.student and not review.student.full_name:
            s_name = review.student.email

        t_name = review.tutor.full_name if review.tutor and review.tutor.full_name else "Tutor"
        if review.tutor and not review.tutor.full_name:
            t_name = review.tutor.email

        results.append({
            "id": review.id,
            "student_id": review.student_id,
            "tutor_id": review.tutor_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at,
            "student_name": s_name,
            "tutor_name": t_name
        })
        
    return results