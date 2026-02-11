from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Follow
from duolingo_app.database.schema import FollowInputSchema, FollowOutSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


follow_router = APIRouter(prefix="/follow", tags=["Follow"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@follow_router.post("/", response_model=FollowOutSchema)
async def create_follow(
    follow: FollowInputSchema,
    db: Session = Depends(get_db),
):
    follow_db = Follow(**follow.dict())
    db.add(follow_db)
    db.commit()
    db.refresh(follow_db)
    return follow_db


@follow_router.get("/", response_model=List[FollowOutSchema])
async def list_follows(db: Session = Depends(get_db)):
    return db.query(Follow).all()


@follow_router.get("/{follow_id}", response_model=FollowOutSchema)
async def detail_follow(follow_id: int, db: Session = Depends(get_db)):
    follow_db = (
        db.query(Follow)
        .filter(Follow.id == follow_id)
        .first()
    )
    if not follow_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return follow_db


@follow_router.put("/{follow_id}", response_model=dict)
async def update_follow(
    follow_id: int,
    follow: FollowInputSchema,
    db: Session = Depends(get_db),
):
    follow_db = (
        db.query(Follow)
        .filter(Follow.id == follow_id)
        .first()
    )
    if not follow_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for follow_key, follow_value in follow.dict().items():
        setattr(follow_db, follow_key, follow_value)

    db.commit()
    db.refresh(follow_db)
    return {"message": "Follow озгорулду"}


@follow_router.delete("/{follow_id}", response_model=dict)
async def delete_follow(
    follow_id: int,
    db: Session = Depends(get_db),
):
    follow_db = (
        db.query(Follow)
        .filter(Follow.id == follow_id)
        .first()
    )
    if not follow_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(follow_db)
    db.commit()
    return {"message": "Follow очурулду"}
