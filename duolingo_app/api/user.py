from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import UserProfile
from duolingo_app.database.schema import UserProfileInputSchema, UserProfileOutSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List
from .auth import get_password_hash


user_router = APIRouter(prefix='/user', tags=['user'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@user_router.get('/', response_model=List[UserProfileOutSchema])
async def list_user(db: Session = Depends(get_db)):
    return db.query(UserProfile).all()

@user_router.get('/{user_id}', response_model=UserProfileOutSchema)
async def detail_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id==user_id).first()

    if not user_db:
        raise HTTPException(detail='no such user', status_code=400)

    return user_db


@user_router.put('/{user_id}', response_model=dict)
def update_user(
    user_id: int,
    user: UserProfileInputSchema,
    db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()

    if not user_db:
        raise HTTPException(status_code=404, detail='no such profile')

    for key, value in user.dict().items():
        if key != 'password':
            setattr(user_db, key, value)

    if user.password:
        user_db.password = get_password_hash(user.password)

    db.commit()
    db.refresh(user_db)

    return {'message': 'changed profile'}


@user_router.delete('/{user_id}', response_model=dict)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.id == user_id).first()

    if not user_db:
        raise HTTPException(detail='no such profile', status_code=404)

    db.delete(user_db)
    db.commit()


    return {'message': 'deleted profile'}
