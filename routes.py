from app import app, db, mail
from flask import render_template, redirect, abort, flash, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from models import User
from forms import LoginForm, RegisterForm, ResetForm, NewPassForm
from werkzeug.security import check_password_hash
from flask_mail import Message
from misc import generate_id, check_confirmed


@app.route("/")
def index():
	if current_user.is_authenticated:
		if current_user.confirmed:
			return render_template("app/user.html")
		else:
			return redirect(url_for('unconfirmed'))
	return render_template("app/index.html")


@app.route("/user/<username>")
@login_required
@check_confirmed
def user(username):
	if current_user.username == username:
		return redirect(url_for('index'))
	user = User.query.filter_by(username=username).first_or_404()
	return render_template("app/user.html", user=user)


@app.route("/settings")
@login_required
@check_confirmed
def settings():
	return render_template("app/settings.html")


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
		user = User(register_form.username.data, register_form.password.data, register_form.email.data)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		return redirect(url_for('send_confirm'))
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
				flash("Ссылка для сброса не действительна. Возможно вы обновили страницу.")
				return redirect(url_for('index'))
			user.confirm_token = "confirmed"
			db.session.commit()
		if new_pass_form.validate_on_submit():
			user = User.query.filter_by(old_token=request.form["hidden_token"]).first()
			user.set_password(new_pass_form.password.data)
			db.session.commit()
			flash("Пароль успешно сброшен.")
			return redirect(url_for('login'))
		else:
			return render_template("auth/new_pass.html", form=new_pass_form, token=token)

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
	msg.body = f"Привет, {user.username}!\nДля сброса пароля перейдите по ссылке ниже. Если вы не запрашивали сброс пароля, проигнорируйте это письмо.\n{link}"
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
	msg.body = f"Привет, {current_user.username}!\nВы недавно зарегистрировались в нашем блоге! Чтобы активировать аккаунт, перейдите по ссылке ниже\n{link}"
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


@app.errorhandler(404)
def not_found(e):
	return render_template("errors/404.html")


@app.errorhandler(403)
def forbidden(e):
	return render_template("errors/403.html")


app.register_error_handler(403, forbidden)
app.register_error_handler(404, not_found)