from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import GroupPeople
from duolingo_app.database.schema import GroupPeopleOutSchema, GroupPeopleInputSchema
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


people_router = APIRouter(prefix="/people", tags=["people"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@people_router.post("/", response_model=GroupPeopleOutSchema)
async def create_people(
    people: GroupPeopleInputSchema,
    db: Session = Depends(get_db),
):
    people_db = GroupPeople(**people.dict())
    db.add(people_db)
    db.commit()
    db.refresh(people_db)
    return people_db


@people_router.get("/", response_model=List[GroupPeopleOutSchema])
async def list_people(db: Session = Depends(get_db)):
    return db.query(GroupPeople).all()


@people_router.get("/{people_id}", response_model=GroupPeopleOutSchema)
async def detail_people(people_id: int, db: Session = Depends(get_db)):
    people_db = (
        db.query(GroupPeople)
        .filter(GroupPeople.id == people_id)
        .first()
    )
    if not people_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return people_db


@people_router.put("/{people_id}", response_model=dict)
async def update_people(
    people_id: int,
    people: GroupPeopleInputSchema,
    db: Session = Depends(get_db),
):
    people_db = (
        db.query(GroupPeople)
        .filter(GroupPeople.id == people_id)
        .first()
    )
    if not people_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for people_key, people_value in people.dict().items():
        setattr(people_db, people_key, people_value)

    db.commit()
    db.refresh(people_db)
    return {"message": "Адамдын маалыматы озгорулду"}


@people_router.delete("/{people_id}", response_model=dict)
async def delete_people(
    people_id: int,
    db: Session = Depends(get_db),
):
    people_db = (
        db.query(GroupPeople)
        .filter(GroupPeople.id == people_id)
        .first()
    )
    if not people_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(people_db)
    db.commit()
    return {"message": "Адамдын маалыматы очурулду"}
