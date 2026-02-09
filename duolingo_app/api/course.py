from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Course
from duolingo_app.database.schema import CourseOutSchema, CourseInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List

course_router = APIRouter(prefix='/course', tags=['Course'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@course_router.post('/', response_model=CourseOutSchema)
async def create_course(course: CourseInputSchema, db: Session = Depends(get_db)):
    course_db = Course(**course.dict())
    db.add(course_db)
    db.commit()
    db.refresh(course_db)

    return course_db

@course_router.get('/', response_model=List[CourseOutSchema])
async def list_course(db: Session = Depends(get_db)):
    return db.query(Course).all()

@course_router.get('/{course_id}/', response_model=CourseOutSchema)
async def detail_course(course_id: int, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(detail='No such Course', status_code=400)

    return course_db

@course_router.put('/{course_id}/', response_model=dict)
async def update_course(course_id: int, course: CourseInputSchema, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
         raise HTTPException(detail='No such Course', status_code=400)

    for key, value in course.dict().items():
        setattr(course_db, key, value)

    db.commit()
    db.refresh(course_db)

    return {'message': 'Course update'}

@course_router.delete('/{course_id}/', response_model=dict)
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(detail='No such Course', status_code=400)

    db.delete(course_db)
    db.commit()

    return {'message': 'Course delete'}
