from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import UserProgress
from duolingo_app.database.schema import UserProgressOutSchema, UserProgressInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


progress_router = APIRouter(prefix='/user_progress', tags=['User progress'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@progress_router.post('/', response_model=UserProgressOutSchema)
async def create_progress(progress: UserProgressInputSchema, db: Session = Depends(get_db)):
    progress_db = UserProgress(**progress.dict())
    db.add(progress_db)
    db.commit()
    db.refresh(progress_db)

    return progress_db

@progress_router.get('/', response_model=List[UserProgressOutSchema])
async def list_progress(db: Session = Depends(get_db)):
    db.query(UserProgress).all()

@progress_router.get('/{progress_id}/', response_model=UserProgressOutSchema)
async def detail_progress(progress_id: int, db: Session = Depends(get_db)):
    progress_db = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not progress_db:
        raise HTTPException(detail='No such UserProgress', status_code=400)

    return progress_db

@progress_router.put('/{progress_id}/', response_model=dict)
async def update_progress(progress_id: int, progress: UserProgressInputSchema, db: Session = Depends(get_db)):
    progress_db = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not progress_db:
        raise HTTPException(detail='No such UserProgress', status_code=400)

    for key, value in progress.dict().items():
        setattr(progress_db, key, value)

    db.commit()
    db.refresh(progress_db)

    return {'message': 'UserProgress update'}

@progress_router.delete('/{progress_id}/', response_model=dict)
async def delete_progress(progress_id: int, db: Session = Depends(get_db)):
    progress_db = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if not progress_db:
        raise HTTPException(detail='No such UserProgress',status_code=400)

    db.delete(progress_db)
    db.commit()

    return {'message': 'UserProgress delete'}
