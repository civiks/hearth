from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ServiceStatus(StrEnum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fs_uniquifier: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(default=True)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    # Marketplace fields — populated for professionals, optional for customers.
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # BYOK — Fernet-encrypted Gemini API key for the agent. Server reads this
    # in `routers/agent.py`; never round-tripped back to the client.
    gemini_api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="user_role", backref="users", lazy="select"
    )


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class UserRole(Base):
    __tablename__ = "user_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    time_required: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Marketplace fields for richer browse UX.
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ServiceProfessional(Base):
    __tablename__ = "service_professional"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"), nullable=False, index=True)
    experience: Mapped[int | None] = mapped_column(Integer, nullable=True)  # years
    approval_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ApprovalStatus.PENDING.value
    )
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped[User] = relationship("User", backref="professionals", lazy="select")
    service: Mapped[Service] = relationship("Service", backref="professionals", lazy="select")


class ServiceRequest(Base):
    __tablename__ = "service_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    professional_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_professional.id"), nullable=True
    )
    date_of_request: Mapped[date] = mapped_column(Date, default=datetime.now, index=True)
    date_of_completion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    service_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ServiceStatus.REQUESTED.value, index=True
    )
    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True)

    service: Mapped[Service] = relationship("Service", backref="requests", lazy="select")
    customer: Mapped[User] = relationship(
        "User", foreign_keys=[customer_id], backref="customer_requests", lazy="select"
    )
    professional: Mapped[ServiceProfessional | None] = relationship(
        "ServiceProfessional", backref="service_requests", lazy="select"
    )

    @property
    def service_name(self) -> str | None:
        return self.service.name if self.service else None


class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    professional_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_professional.id"), nullable=True, index=True
    )
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_request.id"), nullable=True
    )
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

    author: Mapped[User] = relationship("User", foreign_keys=[author_id], lazy="select")

    @property
    def author_name(self) -> str | None:
        return self.author.full_name if self.author else None

    @property
    def author_avatar_url(self) -> str | None:
        return self.author.avatar_url if self.author else None
