from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Lesson
from duolingo_app.database.schema import LessonOutSchema, LessonInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import  Session
from typing import List

lesson_router = APIRouter(prefix='/lesson', tags=['Lesson'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lesson_router.post('/', response_model=LessonOutSchema)
async def create_lesson(lesson: LessonInputSchema, db: Session = Depends(get_db)):
    lesson_db = Lesson(**lesson.dict())
    db.add(lesson_db)
    db.commit()
    db.refresh(lesson_db)

    return lesson_db

@lesson_router.get('/', response_model=List[LessonOutSchema])
async def list_lesson(db: Session = Depends(get_db)):
    return db.query(Lesson).all()

@lesson_router.get('/{lesson_id}/', response_model=LessonOutSchema)
async def detail_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson_db = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson_db:
        raise HTTPException(detail='No such Lesson', status_code=400)

    return lesson_db

@lesson_router.put('/{lesson_id}/', response_model=dict)
async def update_lesson(lesson_id: int, lesson: LessonInputSchema, db: Session = Depends(get_db)):
    lesson_db = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson_db:
        raise HTTPException(detail='No such Lesson', status_code=400)

    for key, value in lesson.dict().items():
        setattr(lesson_id, key, value)

    db.commit()
    db.refresh(lesson_db)

    return {'message': 'Lesson update'}

@lesson_router.delete('/{lesson_id}/', response_model=dict)
async def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson_db = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson_db:
        raise HTTPException(detail='No such Lesson', status_code=400)

    db.delete(lesson_db)
    db.commit()

    return {'message': 'Lesson delete'}