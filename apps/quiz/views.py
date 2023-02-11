# クイズの出題
import random

import openai
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from apps.app import db
from apps.config import QUIZ
from apps.quiz.forms import QuizForm

# APIの設定
openai.api_key = "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"
model_engine = "text-davinci-003"

quiz = Blueprint(
    "quiz",
    __name__,
    template_folder="templates",
)


# クイズアプリのトップページ
@quiz.route("/", methods=["POST", "GET"])
def index():
    return render_template("quiz/index.html")


# 問題画面
@quiz.route("/quiz", methods=["POST", "GET"])
@login_required
def quiz_page():
    form = QuizForm()
    quiz_num = request.cookies.get("quiz_num", 0)
    quiz_num = int(quiz_num)
    
    if quiz_num == 0:
        correct_count = 0
    else :
        correct_count = correct_count

    if quiz_num == 10:
        flash("結果発表！")
        return redirect(url_for("quiz.quiz_result", correct_count = correct_count))

    options = random.sample(QUIZ, 4)
    answer = random.choice(options)
    prompt = "「" + answer + "」が答えとなるような" + answer + "の特徴を使った問題を問題文だけ出力してください。"
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    quiz_prompt = completion.choices[0].text

    form.choice.choices = [(o, o) for o in options]

    if form.validate_on_submit():
        choice = form.choice.data
        if choice == answer:
            correct_count += 1
            quiz_num += 1
            flash("正解!")
        else:
            quiz_num += 1
            flash("不正解…")
        response = redirect(url_for("quiz.quiz_page"))
        response.set_cookie("quiz_num", str(quiz_num))
        return response

    return render_template("quiz/quiz_page.html", form=form, quiz_prompt=quiz_prompt)


# 結果画面
@quiz.route("/quiz/result/<correct_count>")
@login_required
def quiz_result(correct_count):
    if int(current_user.high_score) < correct_count:
        current_user.high_score = correct_count
        db.session.add(current_user)
        db.session.commit()

    quiz_num = request.cookies.get("quiz_num", 0)
    quiz_num = int(quiz_num)
    quiz_num = 0
    response = redirect(url_for("quiz.quiz_result_dis"))
    response.set_cookie("quiz_num", str(quiz_num))
    return response


# 表示
@quiz.route("/quiz/result")
@login_required
def quiz_result_dis():
    correct = int(current_user.high_score)
    return render_template("quiz/result.html", correct=correct)
