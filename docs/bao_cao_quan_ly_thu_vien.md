# BAO CAO PHAN TICH - THIET KE - TRIEN KHAI
## HE THONG QUAN LY THU VIEN DAI HOC

## 1. Muc tieu tai lieu
Tai lieu nay mo ta dung hien trang he thong dang chay trong project hien tai, gom:
- Pham vi nghiep vu da trien khai.
- Thiet ke CSDL va API thuc te.
- Giao dien va luong su dung thuc te.
- Phan quyen dang ap dung.
- Danh sach gioi han va huong mo rong.

Luu y quan trong:
- Day la tai lieu "as-built" (bao cao theo code dang co), khong mo ta cac module chua duoc code trong phien ban hien tai.

---

## 2. Tong quan he thong

### 2.1 Bai toan
Thu vien can mot he thong web de:
- Quan ly doc gia, the thu vien, the loai, dau sach, ban sao sach.
- Quan ly muon/tra theo quy tac nghiep vu.
- Quan ly nhan vien, tai khoan, vai tro.
- Trich xuat bao cao tong hop.

### 2.2 Doi tuong su dung
- Admin (quan tri vien).
- Librarian (thu thu).

### 2.3 Cong nghe
- Backend: FastAPI + SQLAlchemy.
- Database: SQLite.
- Frontend: HTML/CSS/JavaScript (static, goi REST API).
- Tai lieu API: Swagger tai /docs.

---

## 3. Pham vi chuc nang da trien khai

### 3.1 Xac thuc va phan quyen
- Dang nhap bang username/password.
- Tra ve role sau dang nhap.
- Phan quyen theo role cho cac endpoint admin.

### 3.2 Quan ly du lieu nghiep vu
- Reader:
  - Tao, xem danh sach, xem chi tiet, cap nhat, xoa.
- Library Card:
  - Tao, xem danh sach, cap nhat status, xoa.
- Category:
  - Tao, xem danh sach/chi tiet, cap nhat, xoa.
- Book Title:
  - Tao, xem danh sach, cap nhat, xoa.
- Book Copy:
  - Tao, xem danh sach, cap nhat, xoa.

### 3.3 Nghiep vu muon/tra
- Tao phieu muon (1 reader muon 1 copy).
- Tra sach theo borrow id.
- Cap nhat status copy va borrow tu dong.

### 3.4 Bao cao
- Top sach duoc muon nhieu.
- Danh sach doc gia chua tra sach.

### 3.5 Quan tri he thong (admin)
- Quan ly Staff.
- Quan ly UserAccount.

### 3.6 UI/UX nang cao (frontend dang co)
- Dashboard theo tab chuc nang.
- Dark mode, localStorage.
- Toast thong bao.
- Skeleton loading.
- Tooltip, ripple effect, hover/focus/active transitions.
- Modal, dropdown, accordion, carousel.
- Reveal on scroll, smooth scroll.

---

## 4. Business rules dang ap dung trong code

1. Moi reader chi duoc muon 1 cuon tai 1 thoi diem.
2. Reader muon sach phai co the thu vien status = active.
3. Copy chi duoc muon khi status = available.
4. Khong xoa reader neu da co borrow history.
5. Khong xoa category neu da duoc tham chieu boi book title.
6. Khong xoa copy neu dang borrowed.
7. Khong xoa staff neu da co borrow history hoac da gan user account.
8. Moi account gan duy nhat voi 1 staff (staff_id unique).

---

## 5. Actor va Use Case (thuc te)

## 5.1 Actor
- Admin.
- Librarian.

## 5.2 Use case cua Librarian
- Dang nhap he thong.
- CRUD Reader.
- CRUD Library Card.
- CRUD Category.
- CRUD Book Title.
- CRUD Book Copy.
- Tao phieu muon.
- Tra sach.
- Xem bao cao.

## 5.3 Use case cua Admin
- Tat ca use case cua Librarian.
- CRUD Staff.
- CRUD UserAccount.

## 5.4 Use case text diagram
```text
[Librarian] --> (Dang nhap)
[Librarian] --> (Quan ly Reader)
[Librarian] --> (Quan ly Library Card)
[Librarian] --> (Quan ly Category)
[Librarian] --> (Quan ly Book Title)
[Librarian] --> (Quan ly Book Copy)
[Librarian] --> (Muon sach)
[Librarian] --> (Tra sach)
[Librarian] --> (Xem bao cao)

[Admin] --> (Tat ca nghiep vu Librarian)
[Admin] --> (Quan ly Staff)
[Admin] --> (Quan ly UserAccount)
```

---

## 6. Thiet ke CSDL (thuc te tu models.py)

## 6.1 Danh sach bang
1. readers
2. library_cards
3. categories
4. book_titles
5. book_copies
6. borrows
7. staffs
8. user_accounts

## 6.2 Mo ta bang chinh

### readers
- id (PK)
- reader_code (UNIQUE)
- full_name
- class_name
- birth_date
- gender
- status (default: active)
- created_at

### library_cards
- id (PK)
- card_number (UNIQUE)
- reader_id (FK -> readers.id)
- issued_date
- status (default: active)
- created_at

### categories
- id (PK)
- category_code (UNIQUE)
- name
- description

### book_titles
- id (PK)
- title_code (UNIQUE)
- title_name
- publisher
- page_count
- size
- author
- quantity (so luong copy)
- category_id (FK -> categories.id)

### book_copies
- id (PK)
- book_title_id (FK -> book_titles.id)
- book_code (UNIQUE)
- condition_status (default: good)
- import_date
- status (default: available)

### borrows
- id (PK)
- borrow_code (UNIQUE)
- book_copy_id (FK -> book_copies.id)
- reader_id (FK -> readers.id)
- staff_id (FK -> staffs.id)
- borrow_date
- return_date (nullable)
- status (default: borrowed)

### staffs
- id (PK)
- staff_code (UNIQUE)
- full_name
- status (default: active)

### user_accounts
- id (PK)
- username (UNIQUE)
- password
- role
- staff_id (FK -> staffs.id, UNIQUE)
- is_active (default: true)

## 6.3 Quan he
- readers 1-n library_cards
- readers 1-n borrows
- categories 1-n book_titles
- book_titles 1-n book_copies
- book_copies 1-n borrows
- staffs 1-n borrows
- staffs 1-1 user_accounts

---

## 7. API design (thuc te)
Base path: /api/v1

## 7.1 Auth
- POST /auth/login

## 7.2 Readers
- POST /readers
- GET /readers
- GET /readers/{reader_id}
- PUT /readers/{reader_id}
- DELETE /readers/{reader_id}

## 7.3 Library Cards
- POST /library-cards
- GET /library-cards
- PUT /library-cards/{card_id}
- DELETE /library-cards/{card_id}

## 7.4 Categories
- POST /categories
- GET /categories
- GET /categories/{category_id}
- PUT /categories/{category_id}
- DELETE /categories/{category_id}

## 7.5 Book Titles
- POST /book-titles
- GET /book-titles
- PUT /book-titles/{book_title_id}
- DELETE /book-titles/{book_title_id}

## 7.6 Book Copies
- POST /book-copies
- GET /book-copies
- PUT /book-copies/{book_copy_id}
- DELETE /book-copies/{book_copy_id}

## 7.7 Borrow / Return
- POST /borrows
- GET /borrows
- POST /returns

## 7.8 Reports
- GET /reports/top-books?limit=10
- GET /reports/unreturned-readers

## 7.9 Admin only
- Staff:
  - POST /staffs
  - GET /staffs
  - PUT /staffs/{staff_id}
  - DELETE /staffs/{staff_id}
- User Account:
  - POST /user-accounts
  - GET /user-accounts
  - PUT /user-accounts/{account_id}
  - DELETE /user-accounts/{account_id}

---

## 8. Thiet ke giao dien (thuc te)

## 8.1 Trang login
- Form username/password.
- Goi API login.
- Luu token/role/staff info vao localStorage.

## 8.2 Trang dashboard
- Sidebar module theo nghiep vu.
- Header thao tac nhanh (theme/copy endpoint/help/menu).
- Cac tab:
  - Dashboard tong quan.
  - Category / Book Title / Book Copy.
  - Reader / Library Card.
  - Borrow & Return.
  - Reports.
  - Staff (admin).
  - Accounts (admin).

## 8.3 Cac thanh phan UI nang cao
- Toast state.
- Skeleton loading table.
- Modal huong dan.
- Dropdown menu nguoi dung.
- Carousel tips.
- Accordion FAQ.
- Reveal on scroll.

---

## 9. Luong nghiep vu chi tiet (as-built)

## 9.1 Luong khoi tao du lieu
1. Admin dang nhap.
2. Tao category.
3. Tao book title.
4. Tao book copy.
5. Tao reader.
6. Tao library card cho reader.

## 9.2 Luong muon sach
1. Chon reader.
2. He thong kiem tra reader co active card.
3. Chon copy available.
4. He thong kiem tra reader chua co borrow borrowed.
5. Tao borrow, cap nhat copy -> borrowed.

## 9.3 Luong tra sach
1. Chon borrow dang borrowed.
2. Nhap condition_status khi tra.
3. He thong cap nhat borrow -> returned + return_date.
4. He thong cap nhat copy -> available.

---

## 10. Phan quyen va bao mat

## 10.1 Co che hien tai
- Login tra role.
- Frontend an/hien module admin theo role.
- Backend dung header X-Role de cho phep route admin.

## 10.2 Route admin duoc bao ve
- /staffs
- /user-accounts

## 10.3 Han che bao mat hien tai
- Chua dung JWT.
- Mat khau dang luu plain text.
- Chua co audit log.

---

## 11. Kiem thu va xac nhan hoat dong

## 11.1 Smoke test da thuc hien
- Login admin thanh cong.
- Route /staffs tra 403 neu thieu X-Role admin.
- Category CRUD tao/sua/xoa thanh cong.
- Dashboard tab du lieu tai duoc qua API.

## 11.2 Checklist nghiep vu
- Reader CRUD: OK
- LibraryCard CRUD: OK
- Category CRUD: OK
- BookTitle CRUD: OK
- BookCopy CRUD: OK
- Borrow/Return: OK
- Reports: OK
- Staff/UserAccount admin CRUD: OK

---

## 12. Khoang cach giua de xuat ly tuong va phien ban hien tai

Day la cac muc thuoc de xuat thiet ke tong quat, chua co trong code hien tai:
- borrow_items (muon nhieu copy trong 1 phieu).
- return_transactions chi tiet.
- audit_logs.
- JWT auth + refresh token.
- fine amount/overdue engine chi tiet.
- phan trang va filter nang cao o backend.

Huong xu ly:
- Cac muc tren duoc dua vao backlog iteration tiep theo.

---

## 13. Huong phat trien tiep
1. Auth JWT + password hash.
2. Them bang audit_logs.
3. Mo rong model muon nhieu copy (borrow + borrow_items).
4. Overdue policy + fine policy.
5. Pagination/search/sort backend.
6. Export bao cao Excel/PDF.
7. Unit test + integration test + CI/CD.

---

## 14. Ket luan
He thong hien tai da dap ung day du khung nghiep vu cot loi cua quan ly thu vien dai hoc theo pham vi MVP nang cao:
- Day du module du lieu chinh.
- Co phan quyen admin/librarian.
- Co rang buoc muon/tra quan trong.
- Co dashboard giao dien hien dai va kha nang van hanh thuc te.

