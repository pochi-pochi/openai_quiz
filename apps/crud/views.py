from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

from apps.app import db
from apps.crud.forms import UserForm
from apps.crud.models import User

# アプリの作成
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# indexエンドポイント
@crud.route("/")
def index():
    return render_template("crud/index.html")


# ユーザーの新規登録、編集
@crud.route("/users/new", methods=["GET", "POST"])
def create_user():
    form = UserForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data,
        )

        # データベースへの登録
        db.session.add(user)
        db.session.commit()

        # 一覧画面への遷移
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)


# 一覧の取得
@crud.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("crud/index.html", users=users)


# できればここに順位表の表示


# ユーザーの編集画面
@crud.route("users/<user_id>", methods=["POST", "GET"])
@login_required
def edit_user(user_id):
    form = UserForm()
    user = User.query.filter_by(id=user_id).first()

    # 提出された場合、情報の更新
    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        # データの更新
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))

    return render_template("crud/edit.html", user=user, form=form)


# ユーザーの削除
@crud.route("users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("crud.users"))
