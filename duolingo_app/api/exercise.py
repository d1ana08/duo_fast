from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Exercise
from duolingo_app.database.schema import ExerciseOutSchema, ExerciseInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


exercise_router = APIRouter(prefix='/exercise', tags=['Exercise'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@exercise_router.post('/', response_model=ExerciseOutSchema)
async def create_ex(ex: ExerciseInputSchema, db: Session = Depends(get_db)):
    ex_db = Exercise(**ex.dict())
    db.add(ex_db)
    db.commit()
    db.refresh(ex_db)

    return ex_db
@exercise_router.get('/', response_model=List[ExerciseOutSchema])
async def list_ex(db:Session = Depends(get_db)):
    return db.query(Exercise).all()

@exercise_router.get('/{ex_id}/', response_model=ExerciseOutSchema)
async def detail_ex(ex_id: int, db: Session = Depends(get_db)):
    ex_db = db.query(Exercise).filter(Exercise.id == ex_id).first()
    if not ex_db:
        raise HTTPException(detail='No such Exercise', status_code=400)

    return ex_db


@exercise_router.put('/{ex_id}/', response_model=dict)
async def update_ex(ex_id: int, ex: ExerciseInputSchema, db: Session = Depends(get_db)):
    ex_db = db.query(Exercise).filter(Exercise.id == ex_id).first()
    if not ex_db:
        raise HTTPException(detail='No such Exercise', status_code=400)

    for key, value in ex.dict().items():
        setattr(ex_db, key, value)

    db.commit()
    db.refresh(ex_db)

    return {'message': 'Exercise update'}

@exercise_router.delete('/{ex_id}/', response_model=dict)
async def delete_ex(ex_id: int, db: Session = Depends(get_db)):
    ex_db = db.query(Exercise).filter(Exercise.id == ex_id).first()
    if not ex_db:
        raise HTTPException(detail='No such Exercise', status_code=400)

    db.delete(ex_db)
    db.commit()



