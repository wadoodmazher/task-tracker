from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"

db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "dev-secret-key-change-later"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@app.route("/")
@login_required
def home():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
@login_required
def add_task():
    # grab submitted text from the form
    text = request.form.get("content")
    # create a new task with that content
    t = Task(content=text, user_id=current_user.id)
    db.session.add(t)
    db.session.commit()
    return redirect(url_for("home"))

# A route like /delete/<int:task_id> that accepts the task's ID as part of the URL
@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    # Look up that task in the database (Task.query.get(task_id))
    t = Task.query.get(task_id)
    # Delete it (db.session.delete(task), then db.session.commit())
    db.session.delete(t)
    db.session.commit()
    # Redirect back home
    return redirect(url_for("home"))

# complete task method
@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    # find the task
    t = Task.query.get(task_id)
    # flip its 'done' value
    t.done = not t.done
    # save it
    db.session.commit()
    # redirect home
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get submitted user/pass
        username = request.form.get("username")
        password = request.form.get("password")
        # find matching user in db using User.query.filter_by(username=...).first()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # correct login -- need to actually start a session here
            login_user(user)
            return redirect(url_for("home"))
        else:
            # wrong user or pass
            return "Invalid username or password"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)