from fastapi import APIRouter, HTTPException, Depends
from duolingo_app.database.models import PaidSubScription
from duolingo_app.database.schema import (
            PaidSubScriptionOutSchema,PaidSubScriptionInputSchema
)
from duolingo_app.database.db import SessionLocal
from sqlalchemy.orm import Session
from typing import List


paid_subscription_router = APIRouter(
    prefix="/paid-subscription",
    tags=["paid_subscription"],
)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@paid_subscription_router.post(
    "/", response_model=PaidSubScriptionOutSchema
)
async def create_paid_subscription(
    subscription: PaidSubScriptionInputSchema,
    db: Session = Depends(get_db),
):
    subscription_db = PaidSubScription(**subscription.dict())
    db.add(subscription_db)
    db.commit()
    db.refresh(subscription_db)
    return subscription_db


@paid_subscription_router.get(
    "/", response_model=List[PaidSubScriptionOutSchema]
)
async def list_paid_subscriptions(
    db: Session = Depends(get_db),
):
    return db.query(PaidSubScription).all()


@paid_subscription_router.get(
    "/{subscription_id}",
    response_model=PaidSubScriptionOutSchema,
)
async def detail_paid_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
):
    subscription_db = (
        db.query(PaidSubScription)
        .filter(PaidSubScription.id == subscription_id)
        .first()
    )
    if not subscription_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)
    return subscription_db


@paid_subscription_router.put(
    "/{subscription_id}", response_model=dict
)
async def update_paid_subscription(
    subscription_id: int,
    subscription: PaidSubScriptionInputSchema,
    db: Session = Depends(get_db),
):
    subscription_db = (
        db.query(PaidSubScription)
        .filter(PaidSubScription.id == subscription_id)
        .first()
    )
    if not subscription_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    for sub_key, sub_value in subscription.dict().items():
        setattr(subscription_db, sub_key, sub_value)

    db.commit()
    db.refresh(subscription_db)
    return {"message": "Жазылуу жаңыртылды"}


@paid_subscription_router.delete(
    "/{subscription_id}", response_model=dict
)
async def delete_paid_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
):
    subscription_db = (
        db.query(PaidSubScription)
        .filter(PaidSubScription.id == subscription_id)
        .first()
    )
    if not subscription_db:
        raise HTTPException(detail="Мындай маалымат жок", status_code=400)

    db.delete(subscription_db)
    db.commit()
    return {"message": "Жазылуу өчүрүлдү"}
