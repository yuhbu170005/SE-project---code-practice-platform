# LeetCode System - Flask Backend

Hệ thống quản lý bài tập lập trình kiểu LeetCode với giao diện HTML/CSS/JS thuần và backend Flask (Python) kết nối MySQL.

## Tính năng

- ✓ Danh sách bài tập từ MySQL database
- ✓ Filter động theo độ khó (Easy/Medium/Hard)
- ✓ Filter theo danh mục (Array, String, Linked List, Math, Dynamic Programming)
- ✓ Filter theo trạng thái (To Do, In Progress, Completed)
- ✓ Tìm kiếm bài tập theo tiêu đề
- ✓ Tạo bài tập mới (CREATE)
- ✓ Chỉnh sửa bài tập (UPDATE)
- ✓ Xóa bài tập (DELETE)
- ✓ Hiển thị acceptance rate và số lượng submissions
- ✓ Responsive design cho mobile và desktop
- ✓ API JSON endpoint

## Yêu cầu

- Python 3.8+
- MySQL 5.7+ hoặc MariaDB
- pip (Python package manager)

## Cấu trúc Thư mục

\`\`\`
leetcode-system/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (cấu hình database)
├── templates/
│   ├── base.html            # Base template (navbar, footer)
│   ├── index.html           # Danh sách bài tập
│   ├── create.html          # Form tạo bài tập mới
│   └── edit.html            # Form chỉnh sửa bài tập
├── static/
│   └── style.css            # CSS styling
├── database/
│   └── init.sql             # Database schema & sample data
└── README.md                # Documentation này
\`\`\`

## Setup & Cài đặt

### 1. Cài đặt Python

Tải Python 3.8+ từ https://www.python.org

### 2. Cài đặt MySQL

Tải MySQL từ https://www.mysql.com hoặc dùng XAMPP/WAMP

### 3. Clone/Download Project

\`\`\`bash
cd leetcode-system
\`\`\`

### 4. Cài đặt Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 5. Cấu hình Database

Mở file `.env` và chỉnh sửa thông tin MySQL:

\`\`\`env
# MySQL Database Configuration
DB_HOST=localhost
DB_USER=root              # Username MySQL của bạn
DB_PASSWORD=              # Password MySQL của bạn (nếu không có thì để trống)
DB_NAME=leetcode_db
DB_PORT=3306

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
\`\`\`

### 6. Khởi tạo Database

**Cách 1: Dùng MySQL command line**

\`\`\`bash
mysql -u root -p < database/init.sql
\`\`\`

**Cách 2: Dùng MySQL Workbench**

- Mở MySQL Workbench
- File → Open SQL Script → chọn `database/init.sql`
- Nhấn Execute

**Cách 3: Dùng PhpMyAdmin (XAMPP)**

- Mở phpMyAdmin tại http://localhost/phpmyadmin
- Tạo database mới tên `leetcode_db`
- Import file `database/init.sql`

### 7. Chạy Flask Server

\`\`\`bash
python app.py
\`\`\`

Server sẽ chạy trên: **http://localhost:5000**

Mở trình duyệt và truy cập link trên để sử dụng!

## Sử dụng Hệ thống

### Xem danh sách bài tập
1. Truy cập `http://localhost:5000`
2. Tất cả bài tập sẽ load từ database

### Tìm kiếm & Filter
- **Search Box**: Tìm kiếm theo tiêu đề
- **Difficulty**: Easy, Medium, Hard
- **Category**: Array, String, Linked List, Math, Dynamic Programming
- **Status**: To Do, In Progress, Completed
- Nhấn nút "Lọc" để áp dụng filters

### Tạo bài tập mới
1. Nhấn nút "+ Thêm bài tập" ở top navbar
2. Điền form:
   - Tiêu đề (*)
   - Mô tả (*)
   - Độ khó (*)
   - Danh mục (*)
   - Acceptance Rate (%)
   - Submissions
3. Nhấn "Tạo bài tập"

### Chỉnh sửa bài tập
1. Click nút "Sửa" trên bài tập bất kỳ
2. Cập nhật thông tin
3. Nhấn "Cập nhật"

### Xóa bài tập
1. Click nút "Xóa"
2. Xác nhận xóa

## API Endpoints

### GET - Tất cả bài tập (HTML)

\`\`\`http
GET http://localhost:5000/
\`\`\`

Query parameters:
- `search` - Tìm kiếm theo title
- `difficulty` - Easy, Medium, Hard
- `category` - Danh mục
- `status` - To Do, In Progress, Completed

Example:
\`\`\`
http://localhost:5000/?difficulty=Easy&category=Array&search=two
\`\`\`

### GET - API JSON

\`\`\`http
GET http://localhost:5000/api/problems
\`\`\`

Query parameters giống như trên.

Response:
\`\`\`json
[
  {
    "id": 1,
    "title": "Two Sum",
    "description": "Given an array of integers...",
    "difficulty": "Easy",
    "category": "Array",
    "acceptance_rate": 47.3,
    "submissions": 15000000,
    "status": "To Do"
  }
]
\`\`\`

### POST - Tạo bài tập

\`\`\`http
POST http://localhost:5000/create
Content-Type: application/x-www-form-urlencoded

title=New Problem&description=...&difficulty=Medium&category=Array&acceptance_rate=45&submissions=1000
\`\`\`

Redirect về `/` nếu thành công.

### POST - Cập nhật bài tập

\`\`\`http
POST http://localhost:5000/edit/1
\`\`\`

### POST - Xóa bài tập

\`\`\`http
POST http://localhost:5000/delete/1
\`\`\`

## Troubleshooting

### Lỗi: "Can't connect to MySQL server"

Kiểm tra:
1. MySQL service đang chạy không?
   - **Windows**: Task Manager → Services → MySQL80 (hoặc MariaDB)
   - **Linux**: `sudo systemctl status mysql`
   - **Mac**: System Preferences → MySQL

2. Username/password có đúng không? (kiểm tra `.env`)

3. Database `leetcode_db` đã tạo chưa?
   \`\`\`bash
   mysql -u root -p
   > SHOW DATABASES;
   \`\`\`

### Lỗi: "No module named 'flask'"

Chạy lại:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

Hoặc install thủ công:
\`\`\`bash
pip install Flask Flask-CORS mysql-connector-python python-dotenv
\`\`\`

### Lỗi: "Template not found"

Đảm bảo:
- Thư mục `templates/` tồn tại
- Tất cả `.html` files nằm trong `templates/`
- File `style.css` nằm trong `static/`

### Port 5000 đang được sử dụng

Thay port trong `app.py`:
\`\`\`python
app.run(debug=True, host='0.0.0.0', port=5001)  # Đổi từ 5000 thành 5001
\`\`\`

## Development Tips

### Hot Reload
Flask chạy ở `debug=True` nên sẽ tự reload khi code thay đổi.

### Reset Database
\`\`\`bash
mysql -u root -p < database/init.sql
\`\`\`

### Xem SQL Queries (Debug)
Chỉnh sửa `app.py` và thêm print statements:
\`\`\`python
print(f"[DEBUG] Query: {query}")
print(f"[DEBUG] Params: {params}")
\`\`\`

## Production Deployment

Để deploy lên server:

1. Thay `debug=False` trong `app.py`
2. Cài Gunicorn:
   \`\`\`bash
   pip install gunicorn
   \`\`\`

3. Chạy với Gunicorn:
   \`\`\`bash
   gunicorn -w 4 app:app
   \`\`\`

4. Setup Nginx reverse proxy
5. Cấu hình SSL certificate (Let's Encrypt)

## Mở rộng Hệ thống

Có thể thêm:
- Authentication (đăng nhập/đăng ký)
- User profiles & tracking tiến độ
- Integrated code editor
- Test cases cho mỗi bài
- Leaderboard
- Discussions & comments
- Tags & advanced search

## License

MIT
