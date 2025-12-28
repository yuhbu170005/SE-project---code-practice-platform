from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app():
    # DÒNG 1: Khởi tạo ứng dụng Flask
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # DÒNG 2: Cấu hình khóa bí mật từ environment variable
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

    # DÒNG 3: Cấu hình CORS
    CORS(app)

    # 1. Đăng ký Blueprint
    from backend.routes.auth_routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/")

    # 2. Đăng ký Main Blueprint (Trang chủ)
    from backend.routes.main_routes import main_bp  # <--- MỚI

    app.register_blueprint(main_bp)

    from backend.routes.judge_routes import judge_bp

    app.register_blueprint(judge_bp)

    from backend.routes.problem_routes import problem_bp

    # Lưu ý: Không cần set url_prefix='/problems' ở đây
    # VÌ: Trong file problem_routes.py bạn đã tự viết sẵn chữ /problems rồi.
    app.register_blueprint(problem_bp)

    from backend.routes.submission_routes import submission_bp

    app.register_blueprint(submission_bp)
    return app
