from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@app.route("/")
def home():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    # grab submitted text from the form
    text = request.form.get("content")
    # create a new task with that content
    t = Task(content=text, user_id=1)
    db.session.add(t)
    db.session.commit()
    return redirect(url_for("home"))

# A route like /delete/<int:task_id> that accepts the task's ID as part of the URL
@app.route("/delete/<int:task_id>", methods=["POST"])
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
def complete_task(task_id):
    # find the task
    t = Task.query.get(task_id)
    # flip its 'done' value
    t.done = not t.done
    # save it
    db.session.commit()
    # redirect home
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)