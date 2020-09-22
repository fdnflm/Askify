from app import app, db, mail
from flask import render_template, redirect, abort, flash, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from models import User, Question
from forms import LoginForm, RegisterForm, ResetForm, NewPassForm, QuestionForm, AnswerForm, EditForm, EditForm2, EditPhotoForm
from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from flask_mail import Message
from misc import generate_id, check_confirmed
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import os


@app.route("/")
def index():
	if current_user.is_authenticated:
		if current_user.confirmed:
			return redirect(url_for('feed'))
		else:
			return redirect(url_for('unconfirmed'))
	return render_template("app/index.html")


@app.route("/user/<username>", methods=["GET", "POST"])
@app.route("/user/<username>/<list_type>")
@login_required
@check_confirmed
def user(username, list_type=None):
	question_form = QuestionForm()
	user = User.query.filter_by(username=username.lower()).first_or_404()
	info = user.country or user.instagram or user.telegram
	followed_users = user.followed.all()
	followers = user.get_followers()
	if list_type == "followed":
		return render_template("app/followers.html",
								users=followed_users,
								view_user=user,
								questions_amount=current_user.get_questions_amount(),
								list_type=list_type)
	elif list_type == "followers":
		return render_template("app/followers.html",
								users=followers,
								view_user=user,
								questions_amount=current_user.get_questions_amount(),
								list_type=list_type)
	if question_form.validate_on_submit():
		q = Question()
		q.text = question_form.message.data
		q.is_anonymous = question_form.anon.data
		q.user_id = current_user.id
		q.to_user_id = user.id
		db.session.add(q)
		db.session.commit()
		flash(f'Вопрос отправлен пользователю @{username}.')
		return redirect(url_for('user', username=username))
	return render_template("app/user.html",
						   user=user,
						   form=question_form,
						   questions=user.get_questions(),
						   questions_amount=current_user.get_questions_amount(),
						   info=info,
						   followers_amount=len(followers),
						   followed_amount=len(followed_users))


@app.route("/feed")
@login_required
@check_confirmed
def feed():
	return render_template("app/feed.html",
						   questions=current_user.followed_questions()
						   + current_user.get_questions(),
						   questions_amount=current_user.get_questions_amount())


@app.route("/subscriptions")
@login_required
@check_confirmed
def subscriptions():
	return render_template("app/subscriptions.html",
							users=current_user.followed.all(),
							questions_amount=current_user.get_questions_amount())


@app.route("/questions", methods=["GET", "POST"])
@login_required
@check_confirmed
def questions():
	questions = current_user.get_questions(answered=False)
	answer_form = AnswerForm()
	if answer_form.validate_on_submit():
		question = Question.query.filter_by(
			id=request.form["question_id"]).first_or_404()
		question.answer = answer_form.message.data
		question.date_modified = datetime.utcnow()
		db.session.commit()
		flash("Ответ был отправлен")
		return redirect(url_for('questions'))
	return render_template("app/questions.html",
						   form=answer_form,
						   questions=questions)


@app.route("/follow/<username>")
@login_required
@check_confirmed
def follow(username):
	user = User.query.filter_by(username=username).first_or_404()
	if user == current_user:
		flash("Вы не можете подписаться на себя")
		return redirect(url_for('user', username=username))
	if current_user.is_following(user):
		flash("Вы уже подписаны на этого пользователя")
	else:
		current_user.follow(user)
		db.session.commit()
		flash(f"Вы подписаны на @{username} теперь 🎉")
	next_page = request.referrer
	if not next_page:
		next_page = url_for('user', username=username)
	return redirect(next_page)


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first_or_404()
	if user == current_user:
		flash("Вы не можете отписаться от себя")
		return redirect(url_for('user', username=username))
	if not current_user.is_following(user):
		flash("Вы уже отписались от этого пользователя")
	else:
		current_user.unfollow(user)
		db.session.commit()
		flash(f"Вы отписались от @{username} 🙁")
	next_page = request.referrer
	if not next_page:
		next_page = url_for('user', username=username)
	return redirect(next_page)


@app.route("/delete_question/<question_id>")
@login_required
@check_confirmed
def delete_question(question_id):
	question = Question.query.filter_by(id=question_id).first_or_404()
	if question.to_user_id == current_user.id:
		db.session.delete(question)
		db.session.commit()
		flash("Вопрос успешно удалён.")
	else:
		abort(403)
	if request.referrer != url_for('questions'):
		return redirect(request.referrer)
	return redirect(url_for('questions'))


@app.route("/settings", methods=["GET", "POST"])
@login_required
@check_confirmed
def settings():
	edit_profile = EditForm(current_user.username)
	edit_password = EditForm2()
	edit_photo = EditPhotoForm()

	if edit_profile.submit.data and edit_profile.validate():
		if edit_profile.username.data != current_user.username:
				current_user.username = edit_profile.username.data

		current_user.first_name = edit_profile.first_name.data
		current_user.last_name = edit_profile.last_name.data

		regions = []
		regions.append(open("regions/country.csv", "r").readlines())
		if edit_profile.country.data:
			if edit_profile.country.data + "\n" in regions[0]:
				current_user.country = edit_profile.country.data
			else:
				edit_profile.country.errors.append("Такой страны не существует")
		else:
			current_user.country = ""

		regions.append(open("regions/city.csv", "r").readlines())
		if edit_profile.city.data:
			if edit_profile.city.data + "\n" in regions[1]:
				current_user.city = edit_profile.city.data
			else:
				edit_profile.city.errors.append("Такого города не существует")
		else:
			current_user.city = ""

		if current_user.country == "" and current_user.city:
			edit_profile.country.errors.append("Для отображения местоположения поле 'Страна' не может быть пустым")
		
		current_user.instagram = edit_profile.inst.data
		current_user.telegram = edit_profile.telegram.data
		current_user.bio = edit_profile.bio.data
		db.session.commit()
		return redirect(url_for('settings'))

	edit_profile.bio.data = current_user.bio if current_user.bio else ""

	if edit_password.submit2.data and edit_password.validate():
		if edit_password.new_password.data:
			if check_password_hash(current_user.password, edit_password.current_password.data):
				current_user.set_password(edit_password.new_password.data)
				flash("Пароль успешно изменен")
				db.session.commit()
			else:
				flash("Пароли не совпадают")
		return redirect(url_for('settings'))

	if edit_photo.submit3.data and edit_photo.validate():
		avatar = edit_photo.photo.data
		filename = secure_filename(generate_id(6) + ".jpg")
		avatar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
		current_user.avatar_id = filename
		db.session.commit()
		return redirect(url_for('settings'))

	return render_template("app/settings.html",
							user=current_user,
							questions_amount=current_user.get_questions_amount(),
							form=edit_profile,
							edit_pwd=edit_password,
							edit_photo=edit_photo)


@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	login_form = LoginForm()
	if login_form.validate_on_submit():
		user = User.query.filter_by(username=login_form.username.data).first()
		if user and check_password_hash(user.password,
										login_form.password.data):
			login_user(user, remember=login_form.remember.data)
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('index')
			return redirect(next_page)
		else:
			flash("Неправильный логин или пароль")
			return redirect(url_for('login'))
	return render_template("auth/login.html", form=login_form)


@app.route("/register", methods=["GET", "POST"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	register_form = RegisterForm()
	if register_form.validate_on_submit():
		try:
			user = User(register_form.username.data,
						register_form.password.data, 
						register_form.email.data)
			db.session.add(user)
			db.session.commit()
			login_user(user)
			return redirect(url_for('send_confirm'))
		except IntegrityError:
			flash("Пользователь с таким никнеймом или почтой уже существует")
	return render_template("auth/register.html", form=register_form)


@app.route("/reset_password", methods=["GET", "POST"])
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset(token=None):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
		
	new_pass_form = NewPassForm()
	reset_form = ResetForm()

	if token:
		if request.method == "GET":
			user = User.query.filter_by(confirm_token=token).first()
			if not user:
				flash(
					"Ссылка для сброса не действительна. Возможно вы обновили страницу."
				)
				return redirect(url_for('index'))
			user.confirm_token = "confirmed"
			db.session.commit()
		if new_pass_form.validate_on_submit():
			user = User.query.filter_by(
				old_token=request.form["hidden_token"]).first_or_404()
			user.set_password(new_pass_form.password.data)
			db.session.commit()
			flash("Пароль успешно сброшен.")
			return redirect(url_for('login'))
		else:
			return render_template("auth/new_pass.html",
								   form=new_pass_form,
								   token=token)

	if reset_form.validate_on_submit():
		user = User.query.filter_by(email=reset_form.email.data).first()
		if user:
			return redirect(url_for('send_reset', email=reset_form.email.data))
		else:
			flash("Пользователя с таким email не существует.")
	return render_template("auth/reset.html", form=reset_form)


@app.route("/send_reset/<email>")
def send_reset(email):
	msg = Message("Сброс пароля.",
				  recipients=[email],
				  sender=app.config["MAIL_DEFAULT_SENDER"])
	token = generate_id(12)
	link = request.url_root + f"reset_password/{token}"
	user = User.query.filter_by(email=email).first()
	user.confirm_token = token
	user.old_token = token
	db.session.commit()
	msg.html = render_template("email.html",
								username=user.username,
								link=link,
								action="Сбросить пароль",
								reset=1)
	mail.send(msg)
	flash('Для сброса пароля, перейдите по ссылке в письме.')
	return redirect(url_for('index'))


@app.route("/unconfirmed")
@login_required
def unconfirmed():
	if current_user.confirmed == 1:
		return redirect(url_for('index'))
	return render_template("auth/unconfirmed.html")


@app.route("/send_confirm")
@login_required
def send_confirm():
	if current_user.confirmed == 1:
		return redirect(url_for('index'))
	msg = Message("Подтвердите ваш аккаунт.",
				  recipients=[current_user.email],
				  sender=app.config["MAIL_DEFAULT_SENDER"])
	token = generate_id(32)
	link = request.url_root + f"confirm/{token}"
	current_user.confirm_token = token
	db.session.commit()
	msg.html = render_template("email.html",
								username=current_user.username,
								link=link,
								action="Подтвердить аккаунт")
	mail.send(msg)
	return redirect("/unconfirmed")


@app.route("/confirm/<token>")
@login_required
def confirm(token):
	if current_user.confirmed == 1:
		return redirect(url_for('index'))
	user = User.query.filter_by(confirm_token=token).first_or_404()
	user.confirmed = 1
	user.confirm_token = "confirmed"
	db.session.commit()
	return redirect("/")


@app.route('/logout')
def logout():
	logout_user()
	return redirect("/")


@app.before_request
def before_app_request():
	if current_user.is_authenticated and current_user.banned == 1 and not request.url.endswith("/logout"):
		return render_template("errors/banned.html")


@app.errorhandler(404)
def not_found(e):
	return render_template("errors/404.html")


@app.errorhandler(403)
def forbidden(e):
	return render_template("errors/403.html")


app.register_error_handler(403, forbidden)
app.register_error_handler(404, not_found)
