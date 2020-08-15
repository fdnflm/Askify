from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash


followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


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
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=("followers.c.follower_id == User.id"),
		secondaryjoin=("followers.c.followed_id == User.id"),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	def __init__(self, username, password, first_name, last_name, email):
		self.username = username
		self.first_name = first_name
		self.last_name = last_name
		self.password = generate_password_hash(password)
		self.email = email

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def get_questions(self):
		return Question.query.filter_by(to_user_id=self.id).filter(
						Question.answer != None).order_by(
					Question.date_created.desc()).all()

	def get_questions_amount(self):
		return len(
				Question.query.filter_by(to_user_id=self.id).filter(
					Question.answer == None).all())

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0
		
	def followed_questions(self):
		return Question.query.join(
			followers, (followers.c.followed_id == Question.to_user_id)).filter(
				followers.c.follower_id == self.id).order_by(
					Question.date_created.desc()).all()

	def __repr__(self):
		return f"<User {self.username}>"


class Question(Base):
	__tablename__ = "questions"
	text = db.Column(db.String(140))
	answer = db.Column(db.String(512))
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	to_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	main_user = db.relationship(User, foreign_keys=[user_id],
								  backref='questions')
	second_user = db.relationship(User, foreign_keys=[to_user_id])
	is_anonymous = db.Column(db.Integer())

	def __repr__(self):
		return f"<Question {self.id}>"


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)


def init():
	db.create_all()
	admin = User("admin", "password", "Абдул", "Алиев", "test@mail.com")
	admin.confirmed = 1
	user = User("user", "password", "Пётр", "Первый", "123@mail.com")
	user.confirmed = 1
	db.session.add_all([admin, user])
	db.session.commit()

if __name__ == "__main__":
	init()