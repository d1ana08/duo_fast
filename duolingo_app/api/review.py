from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Review
from duolingo_app.database.schema import ReviewInputSchema, ReviewOutSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


review_router = APIRouter(prefix="/review", tags=["review"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@review_router.post("/", response_model=ReviewOutSchema)
async def create_review(
    review: ReviewInputSchema,
    db: Session = Depends(get_db),
):
    review_db = Review(**review.dict())
    db.add(review_db)
    db.commit()
    db.refresh(review_db)
    return review_db


@review_router.get("/", response_model=List[ReviewOutSchema])
async def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()


@review_router.get("/{review_id}", response_model=ReviewOutSchema)
async def detail_review(review_id: int, db: Session = Depends(get_db)):
    review_db = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )
    if not review_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return review_db


@review_router.put("/{review_id}", response_model=dict)
async def update_review(
    review_id: int,
    review: ReviewInputSchema,
    db: Session = Depends(get_db),
):
    review_db = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )
    if not review_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for review_key, review_value in review.dict().items():
        setattr(review_db, review_key, review_value)

    db.commit()
    db.refresh(review_db)
    return {"message": "Review озгорулду"}


@review_router.delete("/{review_id}", response_model=dict)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    review_db = (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )
    if not review_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(review_db)
    db.commit()
    return {"message": "Review очурулду"}
