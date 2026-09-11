from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrackedProduct(Base):
    __tablename__ = "tracked_products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    asin: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    current_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    product_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )