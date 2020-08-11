import string
import random
from flask import redirect
from flask_login import current_user
from functools import wraps


def generate_id(length):
	return "".join(random.choice(string.ascii_letters) for i in range(length))


def check_confirmed(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		if current_user.is_anonymous:
			return redirect("/login")
		if current_user.confirmed == 0:
			return redirect("/unconfirmed")
		return func(*args, **kwargs)

	return wrap