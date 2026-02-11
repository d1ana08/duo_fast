from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import ChatGroup
from duolingo_app.database.schema import ChatGroupOutSchema, ChatGroupInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


group_router = APIRouter(prefix="/group", tags=["ChatGroup"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@group_router.post("/", response_model= ChatGroupOutSchema)
async def create_group(group: ChatGroupInputSchema, db: Session = Depends(get_db)):
    group_db = ChatGroup(**group.dict())
    db.add(group_db)
    db.commit()
    db.refresh(group_db)
    return group_db


@group_router.get("/", response_model=List[ChatGroupOutSchema])
async def list_groups(db: Session = Depends(get_db)):
    return db.query(ChatGroup).all()


@group_router.get("/{group_id}", response_model= ChatGroupOutSchema)
async def detail_group(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return group_db


@group_router.put("/{group_id}", response_model=dict)
async def update_group(
    group_id: int,
    group: ChatGroupInputSchema,
    db: Session = Depends(get_db),
):
    group_db = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for group_key, group_value in group.dict().items():
        setattr(group_db, group_key, group_value)

    db.commit()
    db.refresh(group_db)
    return {"message": "Группа озгорулду"}


@group_router.delete("/{group_id}", response_model=dict)
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(group_db)
    db.commit()
    return {"message": "Группа очурулду"}
