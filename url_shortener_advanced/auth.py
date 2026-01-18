from flask import Blueprint, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
from models import db, User

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.record_once
def on_load(state):
    bcrypt.init_app(state.app)

@auth_bp.route("/", methods=["GET"])
def home():
    return redirect("/login")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not (5 <= len(username) <= 9):
            error = "Username must be 5–9 characters"
        elif User.query.filter_by(username=username).first():
            error = "Username already exists"
        else:
            hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(username=username, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")

    return render_template("signup.html", error=error)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            session.permanent = True
            session["user_id"] = user.id
            return redirect("/dashboard")
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
