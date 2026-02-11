from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import ChatMessage
from duolingo_app.database.schema import ChatMessageOutSchema,ChatMessageInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


message_router = APIRouter(prefix="/message", tags=["message"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@message_router.post("/", response_model=ChatMessageOutSchema)
async def create_message(
    message: ChatMessageInputSchema,
    db: Session = Depends(get_db),
):
    message_db = ChatMessage(**message.dict())
    db.add(message_db)
    db.commit()
    db.refresh(message_db)
    return message_db


@message_router.get("/", response_model=List[ChatMessageOutSchema])
async def list_messages(db: Session = Depends(get_db)):
    return db.query(ChatMessage).all()


@message_router.get("/{message_id}", response_model=ChatMessageOutSchema)
async def detail_message(message_id: int, db: Session = Depends(get_db)):
    message_db = (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id)
        .first()
    )
    if not message_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return message_db


@message_router.put("/{message_id}", response_model=dict)
async def update_message(
    message_id: int,
    message: ChatMessageInputSchema,
    db: Session = Depends(get_db),
):
    message_db = (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id)
        .first()
    )
    if not message_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for message_key, message_value in message.dict().items():
        setattr(message_db, message_key, message_value)

    db.commit()
    db.refresh(message_db)
    return {"message": "Билдирүү озгорулду"}


@message_router.delete("/{message_id}", response_model=dict)
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
):
    message_db = (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id)
        .first()
    )
    if not message_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(message_db)
    db.commit()
    return {"message": "Билдирүү очурулду"}
