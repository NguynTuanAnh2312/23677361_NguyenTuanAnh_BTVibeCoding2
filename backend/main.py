from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

try:
    from .database import Base, engine, get_db
except ImportError:
    # Fallback for direct execution
    from database import Base, engine, get_db

try:
    from .models import (
        BookCopy,
        BookTitle,
        Borrow,
        Category,
        LibraryCard,
        Reader,
        Staff,
        UserAccount,
    )
except ImportError:
    from models import (
        BookCopy,
        BookTitle,
        Borrow,
        Category,
        LibraryCard,
        Reader,
        Staff,
        UserAccount,
    )

try:
    from .schemas import (
        BookCopyCreate,
        BookCopyOut,
        BookCopyUpdate,
        BookTitleCreate,
        BookTitleOut,
        BookTitleUpdate,
        BorrowCreate,
        BorrowOut,
        CategoryCreate,
        CategoryOut,
        CategoryUpdate,
        LibraryCardCreate,
        LibraryCardUpdate,
        LibraryCardOut,
        LoginOut,
        LoginRequest,
        MessageOut,
        ReaderCreate,
        ReaderOut,
        ReaderUpdate,
        ReturnCreate,
        StaffCreate,
        StaffOut,
        StaffUpdate,
        UserAccountCreate,
        UserAccountOut,
        UserAccountUpdate,
    )
except ImportError:
    from schemas import (
        BookCopyCreate,
        BookCopyOut,
        BookCopyUpdate,
        BookTitleCreate,
        BookTitleOut,
        BookTitleUpdate,
        BorrowCreate,
        BorrowOut,
        CategoryCreate,
        CategoryOut,
        CategoryUpdate,
        LibraryCardCreate,
        LibraryCardUpdate,
        LibraryCardOut,
        LoginOut,
        LoginRequest,
        MessageOut,
        ReaderCreate,
        ReaderOut,
        ReaderUpdate,
        ReturnCreate,
        StaffCreate,
        StaffOut,
        StaffUpdate,
        UserAccountCreate,
        UserAccountOut,
        UserAccountUpdate,
    )

Base.metadata.create_all(bind=engine)

app = FastAPI(title="University Library Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_admin(x_role: str | None = Header(default=None, alias="X-Role")) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")


def seed_default_data(db: Session) -> None:
    if db.query(Staff).count() == 0:
        admin_staff = Staff(staff_code="NV001", full_name="Quan tri vien", status="active")
        librarian_staff = Staff(staff_code="NV002", full_name="Thu thu chinh", status="active")
        db.add_all([admin_staff, librarian_staff])
        db.flush()
        db.add_all(
            [
                UserAccount(username="admin", password="admin123", role="admin", staff_id=admin_staff.id),
                UserAccount(
                    username="librarian",
                    password="librarian123",
                    role="librarian",
                    staff_id=librarian_staff.id,
                ),
            ]
        )
        db.commit()


@app.on_event("startup")
def on_startup() -> None:
    db = next(get_db())
    try:
        seed_default_data(db)
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"message": "Library API is running"}


@app.post("/api/v1/auth/login", response_model=LoginOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(UserAccount)
        .filter(UserAccount.username == payload.username, UserAccount.password == payload.password)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user.is_active != "true":
        raise HTTPException(status_code=403, detail="Account is inactive")
    staff = db.query(Staff).filter(Staff.id == user.staff_id).first()
    return {
        "message": "Login successful",
        "role": user.role,
        "username": user.username,
        "staff_id": user.staff_id,
        "staff_name": staff.full_name if staff else None,
    }


# Reader CRUD
@app.post("/api/v1/readers", response_model=ReaderOut)
def create_reader(payload: ReaderCreate, db: Session = Depends(get_db)):
    existing = db.query(Reader).filter(Reader.reader_code == payload.reader_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="reader_code already exists")

    reader = Reader(**payload.model_dump())
    db.add(reader)
    db.commit()
    db.refresh(reader)
    return reader


@app.get("/api/v1/readers", response_model=list[ReaderOut])
def get_readers(db: Session = Depends(get_db)):
    return db.query(Reader).order_by(Reader.id.desc()).all()


@app.get("/api/v1/readers/{reader_id}", response_model=ReaderOut)
def get_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return reader


@app.put("/api/v1/readers/{reader_id}", response_model=ReaderOut)
def update_reader(reader_id: int, payload: ReaderUpdate, db: Session = Depends(get_db)):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(reader, key, value)

    db.commit()
    db.refresh(reader)
    return reader


@app.delete("/api/v1/readers/{reader_id}", response_model=MessageOut)
def delete_reader(reader_id: int, db: Session = Depends(get_db)):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    has_borrow = db.query(Borrow).filter(Borrow.reader_id == reader_id).first()
    if has_borrow:
        raise HTTPException(status_code=400, detail="Cannot delete reader with borrowing history")

    db.delete(reader)
    db.commit()
    return {"message": "Reader deleted"}


# Library card CRUD
@app.post("/api/v1/library-cards", response_model=LibraryCardOut)
def create_library_card(payload: LibraryCardCreate, db: Session = Depends(get_db)):
    existing = db.query(LibraryCard).filter(LibraryCard.card_number == payload.card_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="card_number already exists")

    reader = db.query(Reader).filter(Reader.id == payload.reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    active_card = (
        db.query(LibraryCard)
        .filter(LibraryCard.reader_id == payload.reader_id, LibraryCard.status == "active")
        .first()
    )
    if active_card:
        raise HTTPException(status_code=409, detail="Reader already has active card")

    card = LibraryCard(**payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@app.get("/api/v1/library-cards", response_model=list[LibraryCardOut])
def get_library_cards(db: Session = Depends(get_db)):
    return db.query(LibraryCard).order_by(LibraryCard.id.desc()).all()


@app.put("/api/v1/library-cards/{card_id}", response_model=LibraryCardOut)
def update_library_card_status(card_id: int, payload: LibraryCardUpdate, db: Session = Depends(get_db)):
    card = db.query(LibraryCard).filter(LibraryCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    card.status = payload.status
    db.commit()
    db.refresh(card)
    return card


@app.delete("/api/v1/library-cards/{card_id}", response_model=MessageOut)
def delete_library_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(LibraryCard).filter(LibraryCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    db.delete(card)
    db.commit()
    return {"message": "Library card deleted"}


# Category CRUD
@app.post("/api/v1/categories", response_model=CategoryOut)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.category_code == payload.category_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="category_code already exists")
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.get("/api/v1/categories", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.id.desc()).all()


@app.get("/api/v1/categories/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.put("/api/v1/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/v1/categories/{category_id}", response_model=MessageOut)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    title = db.query(BookTitle).filter(BookTitle.category_id == category_id).first()
    if title:
        raise HTTPException(status_code=400, detail="Cannot delete category with book titles")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}


# Book title CRUD
@app.post("/api/v1/book-titles", response_model=BookTitleOut)
def create_book_title(payload: BookTitleCreate, db: Session = Depends(get_db)):
    existing = db.query(BookTitle).filter(BookTitle.title_code == payload.title_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="title_code already exists")

    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    book_title = BookTitle(**payload.model_dump())
    db.add(book_title)
    db.commit()
    db.refresh(book_title)
    return book_title


@app.get("/api/v1/book-titles", response_model=list[BookTitleOut])
def get_book_titles(db: Session = Depends(get_db)):
    return db.query(BookTitle).order_by(BookTitle.id.desc()).all()


@app.put("/api/v1/book-titles/{book_title_id}", response_model=BookTitleOut)
def update_book_title(book_title_id: int, payload: BookTitleUpdate, db: Session = Depends(get_db)):
    book_title = db.query(BookTitle).filter(BookTitle.id == book_title_id).first()
    if not book_title:
        raise HTTPException(status_code=404, detail="Book title not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(book_title, key, value)
    db.commit()
    db.refresh(book_title)
    return book_title


@app.delete("/api/v1/book-titles/{book_title_id}", response_model=MessageOut)
def delete_book_title(book_title_id: int, db: Session = Depends(get_db)):
    book_title = db.query(BookTitle).filter(BookTitle.id == book_title_id).first()
    if not book_title:
        raise HTTPException(status_code=404, detail="Book title not found")
    db.delete(book_title)
    db.commit()
    return {"message": "Book title deleted"}


# Book copy CRUD
@app.post("/api/v1/book-copies", response_model=BookCopyOut)
def create_book_copy(payload: BookCopyCreate, db: Session = Depends(get_db)):
    existing = db.query(BookCopy).filter(BookCopy.book_code == payload.book_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="book_code already exists")

    book_title = db.query(BookTitle).filter(BookTitle.id == payload.book_title_id).first()
    if not book_title:
        raise HTTPException(status_code=404, detail="Book title not found")

    copy = BookCopy(**payload.model_dump(), status="available")
    db.add(copy)
    book_title.quantity += 1
    db.commit()
    db.refresh(copy)
    return copy


@app.get("/api/v1/book-copies", response_model=list[BookCopyOut])
def get_book_copies(db: Session = Depends(get_db)):
    return db.query(BookCopy).order_by(BookCopy.id.desc()).all()


@app.put("/api/v1/book-copies/{book_copy_id}", response_model=BookCopyOut)
def update_book_copy(book_copy_id: int, payload: BookCopyUpdate, db: Session = Depends(get_db)):
    copy = db.query(BookCopy).filter(BookCopy.id == book_copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(copy, key, value)
    db.commit()
    db.refresh(copy)
    return copy


@app.delete("/api/v1/book-copies/{book_copy_id}", response_model=MessageOut)
def delete_book_copy(book_copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(BookCopy).filter(BookCopy.id == book_copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    if copy.status == "borrowed":
        raise HTTPException(status_code=400, detail="Book copy is being borrowed")

    book_title = db.query(BookTitle).filter(BookTitle.id == copy.book_title_id).first()
    if book_title and book_title.quantity > 0:
        book_title.quantity -= 1

    db.delete(copy)
    db.commit()
    return {"message": "Book copy deleted"}


# Borrow / Return
@app.post("/api/v1/borrows", response_model=BorrowOut)
def create_borrow(payload: BorrowCreate, db: Session = Depends(get_db)):
    reader = db.query(Reader).filter(Reader.id == payload.reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    card = (
        db.query(LibraryCard)
        .filter(LibraryCard.reader_id == payload.reader_id, LibraryCard.status == "active")
        .first()
    )
    if not card:
        raise HTTPException(status_code=400, detail="Reader has no active library card")

    staff = db.query(Staff).filter(Staff.id == payload.staff_id, Staff.status == "active").first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found or inactive")

    copy = db.query(BookCopy).filter(BookCopy.id == payload.book_copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    if copy.status != "available":
        raise HTTPException(status_code=400, detail="Book copy is not available")

    active_borrow = db.query(Borrow).filter(Borrow.reader_id == payload.reader_id, Borrow.status == "borrowed").first()
    if active_borrow:
        raise HTTPException(status_code=400, detail="Each reader can borrow only one book at a time")

    borrow_count = db.query(func.count(Borrow.id)).scalar() or 0
    borrow = Borrow(
        borrow_code=f"BR-{borrow_count + 1:05d}",
        book_copy_id=payload.book_copy_id,
        reader_id=payload.reader_id,
        staff_id=payload.staff_id,
        borrow_date=date.today(),
        status="borrowed",
    )
    db.add(borrow)
    copy.status = "borrowed"

    db.commit()
    db.refresh(borrow)
    return borrow


@app.get("/api/v1/borrows", response_model=list[BorrowOut])
def get_borrows(db: Session = Depends(get_db)):
    return db.query(Borrow).order_by(Borrow.id.desc()).all()


@app.post("/api/v1/returns", response_model=MessageOut)
def return_book(payload: ReturnCreate, db: Session = Depends(get_db)):
    borrow = db.query(Borrow).filter(Borrow.id == payload.borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Borrow not found")
    if borrow.status != "borrowed":
        raise HTTPException(status_code=400, detail="Borrow already returned")

    copy = db.query(BookCopy).filter(BookCopy.id == borrow.book_copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Book copy not found")

    borrow.status = "returned"
    borrow.return_date = date.today()
    copy.status = "available"
    copy.condition_status = payload.condition_status

    db.commit()
    return {"message": "Book returned successfully"}


# Basic reports
@app.get("/api/v1/reports/top-books")
def top_books(limit: int = 10, db: Session = Depends(get_db)):
    rows = (
        db.query(BookTitle.title_name, func.count(Borrow.id).label("borrow_count"))
        .join(BookCopy, BookCopy.book_title_id == BookTitle.id)
        .join(Borrow, Borrow.book_copy_id == BookCopy.id)
        .group_by(BookTitle.id)
        .order_by(func.count(Borrow.id).desc())
        .limit(limit)
        .all()
    )
    return [{"title": row[0], "borrow_count": row[1]} for row in rows]


@app.get("/api/v1/reports/unreturned-readers")
def unreturned_readers(db: Session = Depends(get_db)):
    rows = (
        db.query(Reader.reader_code, Reader.full_name, Borrow.borrow_code, Borrow.borrow_date)
        .join(Borrow, Borrow.reader_id == Reader.id)
        .filter(Borrow.status == "borrowed")
        .order_by(Borrow.borrow_date.asc())
        .all()
    )
    return [
        {
            "reader_code": row[0],
            "full_name": row[1],
            "borrow_code": row[2],
            "borrow_date": row[3],
        }
        for row in rows
    ]


# Staff and account management
@app.post("/api/v1/staffs", response_model=StaffOut)
def create_staff(payload: StaffCreate, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    existing = db.query(Staff).filter(Staff.staff_code == payload.staff_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="staff_code already exists")
    staff = Staff(**payload.model_dump(), status="active")
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@app.get("/api/v1/staffs", response_model=list[StaffOut])
def get_staffs(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return db.query(Staff).order_by(Staff.id.desc()).all()


@app.put("/api/v1/staffs/{staff_id}", response_model=StaffOut)
def update_staff(staff_id: int, payload: StaffUpdate, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff


@app.delete("/api/v1/staffs/{staff_id}", response_model=MessageOut)
def delete_staff(staff_id: int, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    has_borrow = db.query(Borrow).filter(Borrow.staff_id == staff_id).first()
    if has_borrow:
        raise HTTPException(status_code=400, detail="Cannot delete staff with borrow history")

    account = db.query(UserAccount).filter(UserAccount.staff_id == staff_id).first()
    if account:
        raise HTTPException(status_code=400, detail="Cannot delete staff with user account")

    db.delete(staff)
    db.commit()
    return {"message": "Staff deleted"}


@app.post("/api/v1/user-accounts", response_model=UserAccountOut)
def create_user_account(payload: UserAccountCreate, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    existing = db.query(UserAccount).filter(UserAccount.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="username already exists")

    staff = db.query(Staff).filter(Staff.id == payload.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    account = UserAccount(**payload.model_dump(), is_active="true")
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@app.get("/api/v1/user-accounts", response_model=list[UserAccountOut])
def get_user_accounts(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return db.query(UserAccount).order_by(UserAccount.id.desc()).all()


@app.put("/api/v1/user-accounts/{account_id}", response_model=UserAccountOut)
def update_user_account(
    account_id: int,
    payload: UserAccountUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    account = db.query(UserAccount).filter(UserAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


@app.delete("/api/v1/user-accounts/{account_id}", response_model=MessageOut)
def delete_user_account(account_id: int, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    account = db.query(UserAccount).filter(UserAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"message": "Account deleted"}
