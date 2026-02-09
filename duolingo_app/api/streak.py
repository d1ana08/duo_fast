from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Streak
from duolingo_app.database.schema import StreakOutSchema, StreakInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


streak_router = APIRouter(prefix='/streak', tags=['Streak'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@streak_router.post('/', response_model=StreakOutSchema)
async def create_streak(streak: StreakInputSchema, db: Session = Depends(get_db)):
    streak_db = Streak(**streak.dict())
    db.add(streak_db)
    db.commit()
    db.refresh(streak_db)

    return streak_db

@streak_router.get('/', response_model=List[StreakOutSchema])
async def list_streak(db: Session = Depends(get_db)):
    return db.query(Streak).all()

@streak_router.get('/{streak_id}/', response_model=StreakOutSchema)
async def detail_streak(streak_id: int, db: Session = Depends(get_db)):
    streak_db = db.query(Streak).filter(Streak.id == streak_id).first()
    if not streak_db:
        raise HTTPException(detail='No such Streak', status_code=400)

    return streak_db

@streak_router.put('/{streak_id}/', response_model=dict)
async def  update_streak(streak_id: int, streak: StreakInputSchema, db: Session = Depends(get_db)):
    streak_db = db.query(Streak).filter(Streak.id == streak_id).first()
    if not streak_db:
        raise HTTPException(detail='No such Streak',status_code=400)

    for key, value in streak.dict().items():
        setattr(streak_db, key, value)

    db.commit()
    db.refresh(streak_db)

    return {'message': 'Streak update'}


@streak_router.delete('/{streak_id}/', response_model=dict)
async def delete_streak(streak_id: int, db: Session = Depends(get_db)):
    streak_db = db.query(Streak).filter(Streak.id == streak_id).first()
    if not streak_db:
        raise HTTPException(detail='No such Streak', status_code=400)

    db.delete(streak_db)
    db.commit()

    return {'message': 'Streak delete'}