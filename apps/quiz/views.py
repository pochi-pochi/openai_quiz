# クイズの出題
import os
import random

import openai
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from apps.app import db
from apps.config import QUIZ
from apps.quiz.forms import QuizForm

# APIの設定
openai.api_key = os.getenv("OPENAI_API_KEY")
model_engine = "text-davinci-003"

quiz = Blueprint(
    "quiz",
    __name__,
    template_folder="templates",
)

option_num = []
ANSWER = []
prompts = []
correct_or_not = []


# クイズアプリのトップページ
@quiz.route("/", methods=["POST", "GET"])
def index():
    return render_template("quiz/index.html")


# 問題作成画面
@quiz.route("/quiz/make")
@login_required
def quiz_make():
    for i in range(11):
        options = random.sample(QUIZ, 4)
        answer = random.choice(options)
        option_num.append(options)
        ANSWER.append(answer)
        prompt = "「" + ANSWER[i] + "」が答えとなるような" + ANSWER[i] + "の特徴を使った問題を問題文だけ出力してください。"
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        quiz_prompt = completion.choices[0].text
        prompts.append(quiz_prompt)

    correct_count = request.cookies.get("correct_count", 0)
    correct_count = int(correct_count)
    quiz_num = request.cookies.get("quiz_num", 0)
    quiz_num = int(quiz_num)
    correct_count = 0
    quiz_num = 0
    response = redirect(url_for("quiz.quiz_page"))
    response.set_cookie("correct_count", str(correct_count))
    response.set_cookie("quiz_num", str(quiz_num))
    return response


# 問題画面
@quiz.route("/quiz", methods=["POST", "GET"])
@login_required
def quiz_page():
    form = QuizForm()
    quiz_num = request.cookies.get("quiz_num", 0)
    quiz_num = int(quiz_num)
    print(quiz_num)

    if quiz_num == 10:
        flash("結果発表！")
        return redirect(
            url_for(
                "quiz.quiz_result",
                correct_count=correct_count,
                correct_or_not=correct_or_not,
            )
        )

    options = option_num[quiz_num]
    answer = ANSWER[quiz_num]
    quiz_prompt = prompts[quiz_num]

    form.choice.choices = [(o, o) for o in options]

    if form.validate_on_submit():
        choice = form.choice.data
        print(choice, answer, correct_count)
        if choice == answer:
            correct_or_not.append(1)
            correct_count += 1
            quiz_num += 1
            flash("正解!")
        else:
            correct_or_not.append(0)
            quiz_num += 1
            flash("不正解…")
        response = redirect(url_for("quiz.quiz_page"))
        response.set_cookie("quiz_num", str(quiz_num))
        return response

    return render_template("quiz/quiz_page.html", form=form, quiz_prompt=quiz_prompt)


# 結果画面
@quiz.route("/quiz/result/<correct_count>/<correct_or_not>")
@login_required
def quiz_result(correct_count, correct_or_not):
    if int(current_user.high_score) < int(correct_count):
        current_user.high_score = int(correct_count)
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for("quiz.quiz_result_dis", correct_or_not=correct_or_not))


# 表示
@quiz.route("/quiz/result/<correct_or_not>")
@login_required
def quiz_result_dis(correct_or_not):
    correct_or_not = correct_or_not
    correct_sum = 0
    for i in range(30):
        if correct_or_not[i] == "1":
            correct_sum += 1
        else:
            continue
    correct = int(current_user.high_score)
    return render_template(
        "quiz/result.html",
        correct=correct,
        correct_or_not=correct_or_not,
        correct_sum=correct_sum,
    )
