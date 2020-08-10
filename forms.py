from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField 
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
	username = StringField("Имя пользователя", validators=[DataRequired()])
	password = StringField("Пароль", validators=[DataRequired()])
	remember = BooleanField("Запомнить меня")
	submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
	email = StringField("Электронная почта", validators=[DataRequired(), Email(message="Введите верный email адрес")])
	username = StringField("Имя пользователя", validators=[DataRequired()])
	password = StringField("Пароль", validators=[DataRequired(), Length(min=8, message="Длина пароля должна быть больше 8 символов.")])
	password_repeat = StringField("Повторите пароль", validators=[DataRequired(), EqualTo("password", "Пароли должны совпадать.")])
	submit = SubmitField("Создать аккаунт")
