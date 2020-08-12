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
	email = db.Column(db.String(64), unique=True, index=True)
	password = db.Column(db.String(128))
	avatar_id = db.Column(db.String(32), default="default.png")
	bio = db.Column(db.String(140))
	role = db.Column(db.Integer(), default=0)
	confirmed = db.Column(db.Integer(), default=0)
	confirm_token = db.Column(db.String(64), unique=True)
	banned = db.Column(db.Integer(), default=0)
	old_token = db.Column(db.String(64))

	def __init__(self, username, password, email):
		self.username = username
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
	to_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	is_anonymous = db.Column(db.Integer())

	def __repr__(self):
		return f"<Question-{self.id}>"


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)


def init():
	db.create_all()
	user = User("admin", "password", "admin@local.com")
	user.confirmed = 1
	db.session.add(user)
	db.session.commit()


if __name__ == "__main__":
	init()