from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import (
    ProductResponse,
    TrackedProductCreate,
    TrackedProductResponse,
)
from app.models.tracked_product import TrackedProduct
from app.models.user import User
from app.services import amazon


router = APIRouter(tags=["products"])


@router.get(
    "/product/{asin}",
    response_model=ProductResponse,
    summary="Get current name + price for an Amazon.sa product",
)
def get_product(asin: str):
    data = amazon.get_product(asin)
    return ProductResponse(**data)


@router.post(
    "/tracked-products",
    response_model=TrackedProductResponse,
    summary="Add a product to the user's tracking list",
)
def add_tracked_product(
    product: TrackedProductCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == product.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    data = amazon.get_product(product.asin)

    existing_product = (
        db.query(TrackedProduct)
        .filter(
            TrackedProduct.user_id == product.user_id,
            TrackedProduct.asin == product.asin,
        )
        .first()
    )

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="This product is already being tracked.",
        )

    tracked_product = TrackedProduct(
        user_id=product.user_id,
        asin=product.asin,
        product_name=data["product"],
        current_price=data["price"],
        product_url=data["url"],
    )

    db.add(tracked_product)
    db.commit()
    db.refresh(tracked_product)

    return tracked_product


@router.get(
    "/tracked-products/{user_id}",
    response_model=list[TrackedProductResponse],
    summary="Get all tracked products for a user",
)
def get_tracked_products(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    products = (
        db.query(TrackedProduct)
        .filter(TrackedProduct.user_id == user_id)
        .all()
    )

    return products


@router.delete(
    "/tracked-products/{product_id}",
    summary="Remove a tracked product",
)
def delete_tracked_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    tracked_product = (
        db.query(TrackedProduct)
        .filter(TrackedProduct.id == product_id)
        .first()
    )

    if not tracked_product:
        raise HTTPException(
            status_code=404,
            detail="Tracked product not found",
        )

    db.delete(tracked_product)
    db.commit()

    return {
        "message": "Product removed successfully",
        "id": product_id,
    }


@router.post(
    "/check-prices/{user_id}",
    summary="Check prices for one user's tracked products",
)
def check_prices(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    tracked_products = (
        db.query(TrackedProduct)
        .filter(TrackedProduct.user_id == user_id)
        .all()
    )

    results = []

    for tracked_product in tracked_products:
        try:
            data = amazon.get_product(tracked_product.asin)

            old_price = tracked_product.current_price
            new_price = data["price"]

            if new_price < old_price:
                status = "decreased"
            elif new_price > old_price:
                status = "increased"
            else:
                status = "unchanged"

            tracked_product.current_price = new_price
            tracked_product.product_name = data["product"]
            tracked_product.product_url = data["url"]

            results.append(
                {
                    "id": tracked_product.id,
                    "user_id": tracked_product.user_id,
                    "email": user.email,
                    "asin": tracked_product.asin,
                    "product_name": tracked_product.product_name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "status": status,
                    "product_url": tracked_product.product_url,
                }
            )

        except Exception as exc:
            results.append(
                {
                    "id": tracked_product.id,
                    "user_id": tracked_product.user_id,
                    "email": user.email,
                    "asin": tracked_product.asin,
                    "product_name": tracked_product.product_name,
                    "old_price": tracked_product.current_price,
                    "new_price": None,
                    "status": "error",
                    "product_url": tracked_product.product_url,
                    "error": str(exc),
                }
            )

    db.commit()

    return {
        "user_id": user_id,
        "checked": len(tracked_products),
        "products": results,
    }


@router.post(
    "/check-all-prices",
    summary="Check prices for all tracked products",
)
def check_all_prices(
    db: Session = Depends(get_db),
):
    tracked_products = db.query(TrackedProduct).all()

    results = []

    for tracked_product in tracked_products:
        user = (
            db.query(User)
            .filter(User.id == tracked_product.user_id)
            .first()
        )

        try:
            data = amazon.get_product(tracked_product.asin)

            old_price = tracked_product.current_price
            new_price = data["price"]

            if new_price < old_price:
                status = "decreased"
            elif new_price > old_price:
                status = "increased"
            else:
                status = "unchanged"

            tracked_product.current_price = new_price
            tracked_product.product_name = data["product"]
            tracked_product.product_url = data["url"]

            results.append(
                {
                    "id": tracked_product.id,
                    "user_id": tracked_product.user_id,
                    "email": user.email if user else None,
                    "asin": tracked_product.asin,
                    "product_name": tracked_product.product_name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "status": status,
                    "product_url": tracked_product.product_url,
                }
            )

        except Exception as exc:
            results.append(
                {
                    "id": tracked_product.id,
                    "user_id": tracked_product.user_id,
                    "email": user.email if user else None,
                    "asin": tracked_product.asin,
                    "product_name": tracked_product.product_name,
                    "old_price": tracked_product.current_price,
                    "new_price": None,
                    "status": "error",
                    "product_url": tracked_product.product_url,
                    "error": str(exc),
                }
            )

    db.commit()

    return {
        "checked": len(tracked_products),
        "products": results,
    }