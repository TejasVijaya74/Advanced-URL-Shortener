from flask import Flask, redirect, render_template, request, session
from datetime import timedelta
from models import db, URL
from auth import auth_bp
from utils import is_valid_url, generate_short_code

app = Flask(__name__)

# CONFIG 
app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db.init_app(app)
app.register_blueprint(auth_bp)

# DASHBOARD 
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    short_url = None
    error = None

    if request.method == "POST":
        original_url = request.form.get("url")
        custom_code = request.form.get("custom_code")

        if not is_valid_url(original_url):
            error = "Please enter a valid URL (include http:// or https://)"
        else:
            # Custom or auto-generated code
            if custom_code:
                if URL.query.filter_by(short_code=custom_code).first():
                    error = "Custom short code already exists"
                else:
                    short_code = custom_code
            else:
                short_code = generate_short_code()

            if not error:
                new_url = URL(
                    original_url=original_url,
                    short_code=short_code,
                    user_id=session["user_id"]
                )
                db.session.add(new_url)
                db.session.commit()
                short_url = request.host_url + short_code

    urls = URL.query.filter_by(user_id=session["user_id"]).all()

    return render_template(
        "dashboard.html",
        short_url=short_url,
        urls=urls,
        error=error
    )

# REDIRECT
@app.route("/<short_code>")
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()

    if not url:
        return render_template("error.html", message="Short URL not found"), 404

    url.clicks += 1
    db.session.commit()
    return redirect(url.original_url)

# GLOBAL ERROR
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found"), 404

# RUN
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
