from flask_wtf import FlaskForm
from wtforms import RadioField


class QuizForm(FlaskForm):
    choice = RadioField("選択肢", choices=[], coerce=str)
