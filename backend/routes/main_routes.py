# backend/routes/main_routes.py
from flask import Blueprint, render_template

# 1. Tạo Blueprint tên là 'main'
main_bp = Blueprint('main', __name__)

# 2. Định nghĩa Route cho trang chủ (Root URL)
@main_bp.route('/', methods=['GET'])
def home():
    # Flask sẽ tìm file home.html trong thư mục templates
    return render_template('home.html')

# (Ví dụ) Sau này muốn thêm trang About thì viết tiếp ở đây:
# @main_bp.route('/about')
# def about():
#     return render_template('about.html')