from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InstagramCheck, ValidationError
from models import User
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize


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
	username = StringField("Имя пользователя", 
							validators=[
								DataRequired(), 
								Length(min=4, max=16,
								message="Длина имени должна быть меньше 17 символов.")])
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


class EditForm(FlaskForm):
	username = StringField("Имя пользователя", 
							validators=[
								Length(min=4, max=16,
								message="Длина имени пользователя должна быть меньше 17 символов.")
							])
	first_name = StringField("Имя", 
							validators=[
								Length(max=16,
								message="Длина имени должна быть меньше 17 символов.")
							])
	last_name = StringField("Фамилия", 
							validators=[
								Length(max=16,
								message="Длина фамилии должна быть меньше 17 символов.")
							])
	country = StringField("Страна", 
							validators=[
								Length(max=32,
								message="Длина страны должна быть меньше 33 символов.")
							])
	city = StringField("Город", 
							validators=[
								Length(max=32,
								message="Длина города должна быть меньше 33 символов.")])
	inst = StringField("Instagram", 
							validators=[
								Length(max=30,
								message="Длина instagram должна быть меньше 31 символа."),
								InstagramCheck()
							])
	telegram = StringField("Telegram", 
							validators=[
								Length(max=30,
								message="Длина telegram должна быть меньше 31 символа.")
							])
	bio = TextAreaField("О себе", 
							validators=[
								Length(max=80,
								message="Длина био должна быть меньше 81 символа.")
							])
	submit = SubmitField("Сохранить")

	def __init__(self, original_username, *args, **kwargs):
		super(EditForm, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, given_name):
		if given_name.data == self.original_username:
			return True
		else:
			user = User.query.filter_by(username=given_name.data).first()
			if user is not None:
				raise ValidationError('Такое имя пользователя уже существует')


class EditForm2(FlaskForm):
	new_password = PasswordField("Новый пароль",
									validators=[
										DataRequired(),
										Length(min=8,
										message="Длина пароля должна быть больше 8 символов.")
									])
	current_password = PasswordField("Текущий пароль",
						validators=[
							DataRequired(),
						])
	submit2 = SubmitField("Сохранить изменения")


class EditPhotoForm(FlaskForm):
	photo = FileField('image',
				validators=[
					FileAllowed(['jpg', 'jpeg', 'png'],
								'Только фотографии'),
					FileSize(max_size=12582912,
							message="Максимальный размер файла - 12 мб")
				],
				id="profile_image")
	submit3 = SubmitField("Сохранить", id="apply")
