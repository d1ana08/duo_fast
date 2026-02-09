from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import UserProfile
from duolingo_app.database.schema import UserProfileOutSchema, UserProfileInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


user_router = APIRouter(prefix='/user', tags=['User'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@user_router.get('/', response_model=List[UserProfileOutSchema])
async def list_user(db:Session = Depends(get_db)):
    return db.query(UserProfile).all()

@user_router.get('/{user_id}/', response_model=UserProfileOutSchema)
async def detail_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(detail='No such User', status_code=400)

    return user_db

@user_router.put('/{user_id}/', response_model=dict)
async def update_user(user_id: int, user: UserProfileInputSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(detail='No such User', status_code=400)

    for key, value in user.dict().items():
        setattr(user_db, key, value)

    db.commit()
    db.refresh(user_db)

    return {'message': 'User update'}

@user_router.delete('/{user_id}/', response_model=dict)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user_db:
        raise HTTPException(detail='No such User', status_code=400)

    db.delete(user_db)
    db.commit()

    return {'message': 'User Delete'}

