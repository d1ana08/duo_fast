from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import InviteFriend
from duolingo_app.database.schema import InviteFriendInputSchema,InviteFriendOutSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


invited_friend_router = APIRouter(prefix="/invited-friend", tags=["invited_friend"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@invited_friend_router.post("/", response_model=InviteFriendOutSchema)
async def create_invited_friend(
    invited_friend: InviteFriendInputSchema,
    db: Session = Depends(get_db),
):
    invited_friend_db = InviteFriend(**invited_friend.dict())
    db.add(invited_friend_db)
    db.commit()
    db.refresh(invited_friend_db)
    return invited_friend_db


@invited_friend_router.get("/", response_model=List[InviteFriendOutSchema])
async def list_invited_friends(db: Session = Depends(get_db)):
    return db.query(InviteFriend).all()


@invited_friend_router.get("/{invited_friend_id}", response_model=InviteFriendOutSchema)
async def detail_invited_friend(invited_friend_id: int, db: Session = Depends(get_db)):
    invited_friend_db = (
        db.query(InviteFriend)
        .filter(InviteFriend.id == invited_friend_id)
        .first()
    )
    if not invited_friend_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return invited_friend_db


@invited_friend_router.put("/{invited_friend_id}", response_model=dict)
async def update_invited_friend(
    invited_friend_id: int,
    invited_friend: InviteFriendInputSchema,
    db: Session = Depends(get_db),
):
    invited_friend_db = (
        db.query(InviteFriend)
        .filter(InviteFriend.id == invited_friend_id)
        .first()
    )
    if not invited_friend_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for friend_key, friend_value in invited_friend.dict().items():
        setattr(invited_friend_db, friend_key, friend_value)

    db.commit()
    db.refresh(invited_friend_db)
    return {"message": "Чакырылган дос жаңыртылды"}


@invited_friend_router.delete("/{invited_friend_id}", response_model=dict)
async def delete_invited_friend(
    invited_friend_id: int,
    db: Session = Depends(get_db),
):
    invited_friend_db = (
        db.query(InviteFriend)
        .filter(InviteFriend.id == invited_friend_id)
        .first()
    )
    if not invited_friend_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(invited_friend_db)
    db.commit()
    return {"message": "Чакырылган дос өчүрүлдү"}
