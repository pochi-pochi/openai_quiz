# ユーザークラスの定義
# ハイスコアと名前を保存する
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from apps.app import db, login_manager


# 実際のクラス定義
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    high_score = db.Column(db.Integer, default=0)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # passwordセットのためのプロパティ
    @property
    def password(self, password):
        raise AttributeError("読み取り不可")

    # パスワードをハッシュ化してセット
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # パスワードチェック
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ユーザ名の重複チェック
    def is_duplicate_username(self):
        return User.query.filter_by(username=self.username).first() is not None


# ログイン情報の確認
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
