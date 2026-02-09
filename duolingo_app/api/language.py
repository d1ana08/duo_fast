from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import Language
from duolingo_app.database.schema import LanguageOutSchema, LanguageInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List

language_router = APIRouter(prefix='/language', tags=['Language'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@language_router.post('/', response_model=LanguageOutSchema)
async def create_language(language: LanguageInputSchema, db: Session = Depends(get_db)):
    language_db = Language(**language.dict())
    db.add(language_db)
    db.commit()
    db.refresh(language_db)

    return language_db

@language_router.get('/', response_model=List[LanguageOutSchema])
async def list_language(db: Session = Depends(get_db)):
    return db.query(Language).all()


@language_router.get('/{language_id}/', response_model=LanguageOutSchema)
async def detail_language(language_id: int, db: Session = Depends(get_db)):
    language_db = db.query(Language).filter(Language.id == language_id).first()
    if not language_db:
        raise HTTPException(detail='No such Language',status_code=400)

    return language_db

@language_router.put('/{language_id}/', response_model=dict)
async def update_language(language_id: int, language: LanguageInputSchema, db: Session = Depends(get_db)):
    language_db = db.query(Language).filter(Language.id == language_id).first()
    if not language_db:
        raise HTTPException(detail='No such Language', status_code=400)

    for key, value in language.dict().items():
        setattr(language_db, key, value)

    db.commit()
    db.refresh(language_db)

    return {'message': 'Language update'}

@language_router.delete('/{language_id}/', response_model=dict)
async def delete_language(language_id: int, db: Session = Depends(get_db)):
    language_db = db.query(Language).filter(Language.id == language_id).first()
    if not language_db:
        raise HTTPException(detail='No such Language', status_code=400)

    db.delete(language_db)
    db.commit()

    return {'message': 'Language delete'}