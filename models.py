from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash


class Base(db.Model):
	__abstract__ = True
	id = db.Column(db.Integer, primary_key=True)
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(db.DateTime,
	                          default=db.func.current_timestamp(),
	                          onupdate=db.func.current_timestamp())


class User(UserMixin, Base):
	__tablename__ = 'user'
	username = db.Column(db.String(32), unique=True, index=True)
	first_name = db.Column(db.String(32))
	last_name = db.Column(db.String(32))
	email = db.Column(db.String(64), unique=True, index=True)
	password = db.Column(db.String(128))
	avatar_id = db.Column(db.String(32), default="default.png")
	city = db.Column(db.String(32))
	country = db.Column(db.String(32))
	bio = db.Column(db.String(140))
	telegram = db.Column(db.String(32))
	instagram = db.Column(db.String(32))
	twitter = db.Column(db.String(32))
	role = db.Column(db.Integer(), default=0)
	confirmed = db.Column(db.Integer(), default=0)
	confirm_token = db.Column(db.String(64), unique=True)
	banned = db.Column(db.Integer(), default=0)
	old_token = db.Column(db.String(64))
	questions = db.relationship('Question', backref='author', lazy='dynamic')

	def __init__(self, username, password, first_name, last_name, email):
		self.username = username
		self.first_name = first_name
		self.last_name = last_name
		self.password = generate_password_hash(password)
		self.email = email

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def __repr__(self):
		return f"<User-{self.name}>"


class Question(Base):
	__tablename__ = "questions"
	text = db.Column(db.String(140))
	answer = db.Column(db.String(512))
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	to_user_id = db.Column(db.Integer())
	is_anonymous = db.Column(db.Integer())

	def __repr__(self):
		return f"<Question-{self.id}>"


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)


def init():
	db.create_all()


if __name__ == "__main__":
	init()
