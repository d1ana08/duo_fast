from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import SubCourse
from duolingo_app.database.schema import SubCourseOutSchema, SubCourseInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List

sub_router = APIRouter(prefix='/subcourse', tags=['SubCourse'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@sub_router.post('/', response_model=SubCourseOutSchema)
async def create_sub(sub: SubCourseInputSchema, db: Session = Depends(get_db)):
    sub_db = SubCourse(**sub.dict())
    db.add(sub_db)
    db.commit()
    db.refresh(sub_db)

    return sub_db

@sub_router.get('/', response_model=List[SubCourseOutSchema])
async def list_sub(db: Session = Depends(get_db)):
    return db.query(SubCourse).all()

@sub_router.get('/{sub_id}/', response_model=SubCourseOutSchema)
async def detail_sub(sub_id: int, db: Session = Depends(get_db)):
    sub_db = db.query(SubCourse).filter(SubCourse.id == sub_id)
    if not sub_db:
        raise HTTPException(detail='No such SubCourse', status_code=400)

    return sub_db

@sub_router.put('/{sub_id}/', response_model=dict)
async def update_sub(sub_id: int, sub: SubCourseInputSchema, db: Session = Depends(get_db)):
    sub_db = db.query(SubCourse).filter(SubCourse.id == sub_id).first()
    if not sub_db:
        raise HTTPException(detail='No such SubCourse', status_code=400)

    for key, value in sub.dict().items():
        setattr(sub_db, key, value)

    db.commit()
    db.refresh(sub_db)

    return {'message': 'SubCourse update'}

@sub_router.delete('/{sub_id}/', response_model=dict)
async def delete_sub(sub_id: int, db: Session = Depends(get_db)):
    sub_db = db.query(SubCourse).filter(SubCourse.id == sub_id).first()
    if not sub_db:
        raise HTTPException(detail='No such SubCourse', status_code=400)

    db.delete(sub_db)
    db.commit()

    return {'message': 'SubCourse delete'}
