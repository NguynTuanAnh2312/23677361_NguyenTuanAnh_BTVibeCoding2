# 📚 VibeLib - Hệ Thống Quản Lý Thư Viện Đại Học
## 📌 Mục Lục
- [Giới Thiệu Dự Án](#-giới-thiệu-dự-án)
- [✨ Tính Năng Chính](#-tính-năng-chính)
- [📊 Database Schema](#-database-schema)
- [📋 Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
- [🚀 Hướng Dẫn Cài Đặt](#-hướng-dẫn-cài-đặt)
- [🔐 Tài Khoản Mặc Định](#-tài-khoản-mặc-định)
- [📁 Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [👥 Hướng Dẫn Sử Dụng Chi Tiết](#-hướng-dẫn-sử-dụng-chi-tiết)
- [🎯 Quyền Hạn Người Dùng](#-quyền-hạn-người-dùng)
- [🧩 Danh Sách API Chính](#-danh-sách-api-chính)
- [🔧 Khắc Phục Sự Cố](#-khắc-phục-sự-cố)
- [🧪 Kiểm Thử Nhanh](#-kiểm-thử-nhanh)
- [🛣️ Hướng Phát Triển Tiếp](#️-hướng-phát-triển-tiếp)

## 🎯 Giới Thiệu Dự Án
**VibeLib** là hệ thống quản lý thư viện đại học theo mô hình web full-stack.

Mục tiêu:
- Số hóa quy trình quản lý thư viện.
- Quản lý đầy đủ vòng đời dữ liệu: Độc giả -> Thẻ -> Sách -> Mượn/Trả -> Báo cáo.
- Áp dụng phân quyền rõ ràng giữa **Admin** và **Librarian (Thủ thư)**.
- Tối ưu trải nghiệm người dùng với giao diện hiện đại, responsive, nhiều micro-interactions.

## ✨ Tính Năng Chính

### 1) Nghiệp vụ cơ bản (Core)
- Đăng nhập hệ thống.
- CRUD Độc giả.
- CRUD Thẻ thư viện.
- CRUD Thể loại sách.
- CRUD Đầu sách.
- CRUD Bản sao sách.
- Tạo phiếu mượn.
- Trả sách.
- Báo cáo top sách mượn nhiều.
- Báo cáo độc giả chưa trả sách.

### 2) Nghiệp vụ nâng cao và ràng buộc dữ liệu
- Mỗi độc giả chỉ được mượn **1 cuốn tại 1 thời điểm**.
- Chỉ được mượn khi:
  - Độc giả tồn tại.
  - Có thẻ thư viện active.
  - Bản sao sách ở trạng thái available.
  - Nhân viên xử lý đang active.
- Không cho xóa dữ liệu khi vi phạm ràng buộc tham chiếu:
  - Reader đã có lịch sử mượn.
  - Category đang chứa BookTitle.
  - BookCopy đang borrowed.
  - Staff đã có account hoặc lịch sử mượn.

### 3) UX/UI chuyên nghiệp
- Dashboard theo tab nghiệp vụ.
- Dark mode và lưu trạng thái bằng localStorage.
- Skeleton loading cho bảng dữ liệu.
- Toast message theo trạng thái API (success/warning/error).
- Tooltip, ripple effect, hover/focus/active transitions.
- Modal hướng dẫn nhanh.
- Dropdown menu người dùng.
- Accordion FAQ.
- Carousel mẹo sử dụng.
- Reveal on scroll + smooth scroll.
- Gradient background động nhẹ.

## 📊 Database Schema

### 1) Các bảng chính
- `readers`
- `library_cards`
- `categories`
- `book_titles`
- `book_copies`
- `borrows`
- `staffs`
- `user_accounts`

### 2) Sơ đồ quan hệ (ERD rút gọn)
```mermaid
erDiagram
    READERS ||--o{ LIBRARY_CARDS : owns
    READERS ||--o{ BORROWS : creates
    STAFFS ||--o{ BORROWS : handles
    STAFFS ||--|| USER_ACCOUNTS : has
    CATEGORIES ||--o{ BOOK_TITLES : groups
    BOOK_TITLES ||--o{ BOOK_COPIES : contains
    BOOK_COPIES ||--o{ BORROWS : borrowed_in

    READERS {
      int id PK
      string reader_code UK
      string full_name
      string class_name
      date birth_date
      string gender
      string status
      datetime created_at
    }

    LIBRARY_CARDS {
      int id PK
      string card_number UK
      int reader_id FK
      date issued_date
      string status
      datetime created_at
    }

    CATEGORIES {
      int id PK
      string category_code UK
      string name
      string description
    }

    BOOK_TITLES {
      int id PK
      string title_code UK
      string title_name
      string author
      string publisher
      int page_count
      string size
      int quantity
      int category_id FK
    }

    BOOK_COPIES {
      int id PK
      int book_title_id FK
      string book_code UK
      string condition_status
      date import_date
      string status
    }

    BORROWS {
      int id PK
      string borrow_code UK
      int book_copy_id FK
      int reader_id FK
      int staff_id FK
      date borrow_date
      date return_date
      string status
    }

    STAFFS {
      int id PK
      string staff_code UK
      string full_name
      string status
    }

    USER_ACCOUNTS {
      int id PK
      string username UK
      string password
      string role
      int staff_id FK_UK
      string is_active
    }
```

### 3) Quy tắc dữ liệu quan trọng
- `user_accounts.staff_id` là duy nhất: mỗi nhân viên chỉ gắn tối đa 1 tài khoản.
- `book_titles.quantity` tăng/giảm theo số lượng `book_copies`.
- `borrows.status` chuyển `borrowed` -> `returned` khi trả sách.

## 📋 Yêu Cầu Hệ Thống

### Môi trường tối thiểu
- OS: Windows / Linux / macOS
- Python: 3.10 trở lên
- Trình duyệt hiện đại: Chrome, Edge, Firefox
- Khuyến nghị: VS Code + Live Server

### Dependency backend
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic

### Cổng sử dụng mặc định
- Backend API: `http://127.0.0.1:8000`
- Frontend static (Live Server ví dụ): `http://127.0.0.1:5500`

## 🚀 Hướng Dẫn Cài Đặt

### Bước 1: Tạo môi trường ảo
```powershell
python -m venv .venv
```

### Bước 2: Cài thư viện
```powershell
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
```

### Bước 3: Chạy backend
**Cách khuyến nghị**
```powershell
.venv/Scripts/python.exe run_server.py
```

**Hoặc chạy bằng uvicorn**
```powershell
.venv/Scripts/python.exe -m uvicorn backend.main:app --reload
```

### Bước 4: Truy cập API docs
- Swagger: `http://127.0.0.1:8000/docs`

### Bước 5: Chạy frontend
- Mở file `frontend/login.html` bằng Live Server hoặc static server bất kỳ.
- Frontend gọi API tại: `http://127.0.0.1:8000/api/v1`

## 🔐 Tài Khoản Mặc Định
Tài khoản được seed tự động khi backend chạy lần đầu.

### Admin
- username: `admin`
- password: `admin123`
- role: `admin`

### Librarian
- username: `librarian`
- password: `librarian123`
- role: `librarian`

## 📁 Cấu Trúc Dự Án
```text
23677361_NguyenTuanAnh_BTVibeCoding2/
├─ backend/
│  ├─ main.py              # API routes + business rules
│  ├─ models.py            # SQLAlchemy models
│  ├─ schemas.py           # Pydantic schemas
│  ├─ database.py          # DB engine/session/base
│  ├─ requirements.txt
│  └─ library_v2.db        # SQLite data file
├─ frontend/
│  ├─ login.html           # Trang đăng nhập
│  └─ dashboard.html       # Dashboard + các module CRUD/report
├─ docs/
│  └─ bao_cao_quan_ly_thu_vien.md
├─ run_server.py           # Entry point chạy backend nhanh
└─ README.md
```

## 👥 Hướng Dẫn Sử Dụng Chi Tiết

### Luồng 1: Khởi tạo dữ liệu chuẩn
1. Đăng nhập bằng Admin.
2. Vào **Thể loại sách** -> thêm category.
3. Vào **Đầu sách** -> thêm title và gắn category.
4. Vào **Bản sao sách** -> thêm copy cho từng title.
5. Vào **Độc giả** -> thêm reader.
6. Vào **Thẻ thư viện** -> cấp thẻ cho reader.

### Luồng 2: Mượn sách
1. Vào tab **Mượn/Trả**.
2. Chọn độc giả và chọn bản sao available.
3. Bấm tạo phiếu mượn.
4. Hệ thống tự cập nhật:
   - Borrow status = borrowed
   - BookCopy status = borrowed

### Luồng 3: Trả sách
1. Trong danh sách phiếu mượn, chọn phiếu đang borrowed.
2. Bấm trả sách và nhập condition_status.
3. Hệ thống tự cập nhật:
   - Borrow status = returned
   - Return date = ngày hiện tại
   - BookCopy status = available

### Luồng 4: Báo cáo
1. Tab **Báo cáo** -> chọn giới hạn top sách.
2. Xem:
   - Top sách được mượn nhiều.
   - Danh sách độc giả chưa trả.

## 🎯 Quyền Hạn Người Dùng

### Admin
- Toàn quyền dữ liệu nghiệp vụ (độc giả, sách, mượn/trả, báo cáo).
- Quản lý nhân viên (`/staffs`).
- Quản lý tài khoản (`/user-accounts`).
- Quản lý trạng thái account và role.

### Librarian
- Quản lý nghiệp vụ thư viện hàng ngày:
  - Reader, Card, Category, BookTitle, BookCopy
  - Borrow / Return
  - Reports
- Không có quyền truy cập module Admin.

## 🧩 Danh Sách API Chính
Base URL: `/api/v1`

### Auth
- `POST /auth/login`

### Readers
- `POST /readers`
- `GET /readers`
- `GET /readers/{reader_id}`
- `PUT /readers/{reader_id}`
- `DELETE /readers/{reader_id}`

### Library Cards
- `POST /library-cards`
- `GET /library-cards`
- `PUT /library-cards/{card_id}`
- `DELETE /library-cards/{card_id}`

### Categories
- `POST /categories`
- `GET /categories`
- `GET /categories/{category_id}`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

### Book Titles
- `POST /book-titles`
- `GET /book-titles`
- `PUT /book-titles/{book_title_id}`
- `DELETE /book-titles/{book_title_id}`

### Book Copies
- `POST /book-copies`
- `GET /book-copies`
- `PUT /book-copies/{book_copy_id}`
- `DELETE /book-copies/{book_copy_id}`

### Borrow / Return
- `POST /borrows`
- `GET /borrows`
- `POST /returns`

### Reports
- `GET /reports/top-books?limit=10`
- `GET /reports/unreturned-readers`

### Admin only
- Staffs: `POST/GET/PUT/DELETE /staffs...`
- User accounts: `POST/GET/PUT/DELETE /user-accounts...`

## 🔧 Khắc Phục Sự Cố

### 1) Không đăng nhập được
Nguyên nhân thường gặp:
- Backend chưa chạy.
- Sai username/password.
- Tài khoản bị `is_active = false`.

Cách xử lý:
1. Kiểm tra `http://127.0.0.1:8000/` có trả về JSON không.
2. Kiểm tra tài khoản mặc định ở mục `Tài Khoản Mặc Định`.
3. Mở Swagger và test `POST /auth/login`.

### 2) Lỗi CORS / Failed to fetch
Nguyên nhân:
- Frontend chạy domain khác backend.
- Backend không sẵn sàng.

Cách xử lý:
1. Chạy backend trước frontend.
2. Dùng đúng endpoint `http://127.0.0.1:8000/api/v1`.

### 3) Port 8000 đã được sử dụng
Triệu chứng:
- Uvicorn báo lỗi bind port 8000.

Cách xử lý:
```powershell
# Tìm process đang nghe port 8000
Get-NetTCPConnection -LocalPort 8000 -State Listen

# Dừng process theo PID
Stop-Process -Id <PID> -Force
```

### 4) Dữ liệu bảng không hiển thị
Nguyên nhân:
- API trả lỗi 403 do thiếu quyền admin.
- Dữ liệu chưa được tạo.

Cách xử lý:
1. Kiểm tra role đăng nhập.
2. Tạo dữ liệu theo luồng khởi tạo.
3. Xem toast lỗi trên giao diện và DevTools Console.

### 5) Giao diện không cập nhật sau khi sửa code
Cách xử lý:
- Reload cứng: `Ctrl + F5`
- Kiểm tra cache trình duyệt.

## 🧪 Kiểm Thử Nhanh

Checklist smoke test:
- [ ] Đăng nhập Admin thành công.
- [ ] Tạo Category -> Title -> Copy thành công.
- [ ] Tạo Reader + Card thành công.
- [ ] Tạo Borrow thành công.
- [ ] Reader không thể mượn cuốn thứ 2 khi chưa trả.
- [ ] Trả sách thành công, copy quay lại available.
- [ ] Báo cáo top books hiển thị dữ liệu.
- [ ] Báo cáo unreturned readers hiển thị đúng.
- [ ] Admin xem được Staff/Accounts.
- [ ] Librarian không truy cập được module Admin.

## 🛣️ Hướng Phát Triển Tiếp
- Nâng cấp auth sang JWT + refresh token.
- RBAC đầy đủ theo permission matrix.
- Phân trang, lọc nâng cao, sort nhiều tiêu chí.
- Export Excel/PDF cho báo cáo.
- Dashboard chart trực quan (line/bar/pie).
- Unit test + integration test + CI/CD.
- Docker hoá toàn bộ hệ thống.

---

## 👨‍💻 Thông Tin Thực Hiện
- Tác giả: Nguyễn Tuấn Anh
- Mã sinh viên: 23677361
- Môn học: Phát triển ứng dụng
- Loại dự án: Bài tập lớn / báo cáo hệ thống quản lý thư viện

> Ghi chú: Tài liệu phân tích/thết kế chi tiết xem thêm tại `docs/bao_cao_quan_ly_thu_vien.md`.
