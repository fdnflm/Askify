from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
	username = StringField("Имя пользователя", validators=[DataRequired()])
	password = PasswordField("Пароль", validators=[DataRequired()])
	remember = BooleanField("Запомнить меня")
	submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
	email = StringField("Электронная почта",
						validators=[
							DataRequired(),
							Email(message="Введите верный email адрес")
						])
	username = StringField("Имя пользователя", validators=[DataRequired()])
	password = PasswordField(
		"Пароль",
		validators=[
			DataRequired(),
			Length(min=8,
				   message="Длина пароля должна быть больше 8 символов.")
		])
	password_repeat = PasswordField("Повторите пароль",
									validators=[
										DataRequired(),
										EqualTo("password",
												"Пароли должны совпадать.")
									])
	submit = SubmitField("Создать аккаунт")


class ResetForm(FlaskForm):
	email = StringField("Электронная почта",
						validators=[
							DataRequired(),
							Email(message="Введите верный email адрес")
						])
	submit = SubmitField("Сбросить пароль")


class NewPassForm(FlaskForm):
	password = PasswordField(
		"Пароль",
		validators=[
			DataRequired(),
			Length(min=8,
				   message="Длина пароля должна быть больше 8 символов.")
		])
	password_repeat = PasswordField("Повторите пароль",
									validators=[
										DataRequired(),
										EqualTo("password",
												"Пароли должны совпадать.")
									])
	submit = SubmitField("Сбросить пароль")


class QuestionForm(FlaskForm):
	message = TextAreaField('Вопрос',
							validators=[
								DataRequired(),
								Length(
									max=140,
									message="Максимальная длина 140 символов.")
							])
	anon = BooleanField("Анонимно", id="anon")
	submit = SubmitField('Отправить')


class AnswerForm(FlaskForm):
	message = StringField('Ответ',
						  validators=[
							  DataRequired(),
							  Length(
								  max=140,
								  message="Максимальная длина 140 символов.")
						  ])
	submit = SubmitField('Отправить')
