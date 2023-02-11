# ルートの設定とか
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from apps.config import config

db = SQLAlchemy()

csrf = CSRFProtect()

# loginmanegerのインスタンス化
login_manager = LoginManager()


# appのインスタンス化
def create_app(config_key):
    app = Flask(__name__)

    # config設定とその他設定
    app.config.from_object(config[config_key])
    csrf.init_app(app)
    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    # 各アプリの登録
    from apps.crud import views as crud_views

    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    from apps.auth import views as auth_views

    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    from apps.quiz import views as quiz_views

    app.register_blueprint(quiz_views.quiz, url_prefix="/")

    return app
