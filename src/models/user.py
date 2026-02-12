"""
User model for future multi-tenancy support.
"""

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class User(BaseModel):
    """
    User/Business model for multi-tenancy support.

    This model will be used in future phases to support
    multiple businesses/users on the same platform.
    """

    __tablename__ = "users"

    # Business/User information
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Business information
    business_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    business_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Settings (JSON for flexibility)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, name={self.name})"
