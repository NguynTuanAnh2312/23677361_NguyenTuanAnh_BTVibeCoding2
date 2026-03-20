from datetime import date, datetime

from pydantic import BaseModel, Field


class ReaderBase(BaseModel):
    reader_code: str = Field(min_length=2, max_length=20)
    full_name: str = Field(min_length=2, max_length=120)
    class_name: str
    birth_date: date
    gender: str
    status: str = "active"


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    full_name: str | None = None
    class_name: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    status: str | None = None


class ReaderOut(ReaderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    category_code: str
    name: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryOut(CategoryCreate):
    id: int

    class Config:
        from_attributes = True


class BookTitleBase(BaseModel):
    title_code: str
    title_name: str
    publisher: str
    page_count: int = Field(ge=1)
    size: str
    author: str
    quantity: int = Field(ge=0)
    category_id: int


class BookTitleCreate(BookTitleBase):
    pass


class BookTitleUpdate(BaseModel):
    title_name: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    size: str | None = None
    author: str | None = None
    quantity: int | None = None
    category_id: int | None = None


class BookTitleOut(BaseModel):
    id: int
    title_code: str
    title_name: str
    publisher: str
    page_count: int
    size: str
    author: str
    quantity: int
    category_id: int

    class Config:
        from_attributes = True


class BookCopyCreate(BaseModel):
    book_title_id: int
    book_code: str
    condition_status: str = "good"
    import_date: date


class BookCopyUpdate(BaseModel):
    condition_status: str | None = None
    status: str | None = None


class BookCopyOut(BaseModel):
    id: int
    book_title_id: int
    book_code: str
    condition_status: str
    import_date: date
    status: str

    class Config:
        from_attributes = True


class BorrowCreate(BaseModel):
    book_copy_id: int
    reader_id: int
    staff_id: int


class BorrowOut(BaseModel):
    id: int
    borrow_code: str
    book_copy_id: int
    reader_id: int
    staff_id: int
    borrow_date: date
    return_date: date | None = None
    status: str

    class Config:
        from_attributes = True


class ReturnCreate(BaseModel):
    borrow_id: int
    condition_status: str = "good"

    class Config:
        from_attributes = True


class LibraryCardCreate(BaseModel):
    card_number: str
    reader_id: int
    issued_date: date


class LibraryCardOut(BaseModel):
    id: int
    card_number: str
    reader_id: int
    issued_date: date
    status: str

    class Config:
        from_attributes = True


class StaffCreate(BaseModel):
    staff_code: str
    full_name: str


class StaffUpdate(BaseModel):
    full_name: str | None = None
    status: str | None = None


class StaffOut(BaseModel):
    id: int
    staff_code: str
    full_name: str
    status: str

    class Config:
        from_attributes = True


class UserAccountCreate(BaseModel):
    username: str
    password: str
    role: str
    staff_id: int


class UserAccountOut(BaseModel):
    id: int
    username: str
    role: str
    staff_id: int
    is_active: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    message: str
    role: str
    username: str | None = None
    staff_id: int | None = None
    staff_name: str | None = None


class UserAccountUpdate(BaseModel):
    password: str | None = None
    role: str | None = None
    is_active: str | None = None


class LibraryCardUpdate(BaseModel):
    status: str


class MessageOut(BaseModel):
    message: str
