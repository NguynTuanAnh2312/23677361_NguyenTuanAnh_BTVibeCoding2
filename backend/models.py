from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Reader(Base):
    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reader_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    class_name: Mapped[str] = mapped_column(String(30), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    cards = relationship("LibraryCard", back_populates="reader", cascade="all, delete-orphan")
    borrows = relationship("Borrow", back_populates="reader")


class LibraryCard(Base):
    __tablename__ = "library_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    card_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    reader = relationship("Reader", back_populates="cards")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    book_titles = relationship("BookTitle", back_populates="category")


class BookTitle(Base):
    __tablename__ = "book_titles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title_name: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher: Mapped[str] = mapped_column(String(150), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="book_titles")
    copies = relationship("BookCopy", back_populates="book_title", cascade="all, delete-orphan")


class BookCopy(Base):
    __tablename__ = "book_copies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_title_id: Mapped[int] = mapped_column(ForeignKey("book_titles.id"), nullable=False)
    book_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    condition_status: Mapped[str] = mapped_column(String(30), default="good", nullable=False)
    import_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False)

    book_title = relationship("BookTitle", back_populates="copies")
    borrows = relationship("Borrow", back_populates="book_copy")


class Staff(Base):
    __tablename__ = "staffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    staff_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    borrows = relationship("Borrow", back_populates="staff")
    user_account = relationship("UserAccount", back_populates="staff", uselist=False)


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staffs.id"), unique=True, nullable=False)
    is_active: Mapped[str] = mapped_column(String(10), default="true", nullable=False)

    staff = relationship("Staff", back_populates="user_account")


class Borrow(Base):
    __tablename__ = "borrows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    borrow_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    book_copy_id: Mapped[int] = mapped_column(ForeignKey("book_copies.id"), nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staffs.id"), nullable=False)
    borrow_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="borrowed", nullable=False)

    book_copy = relationship("BookCopy", back_populates="borrows")
    reader = relationship("Reader", back_populates="borrows")
    staff = relationship("Staff", back_populates="borrows")
