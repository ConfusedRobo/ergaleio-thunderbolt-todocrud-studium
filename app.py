from datetime import datetime

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo_db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(app)


class Todo(database.Model):
    identity = database.Column(database.Integer, primary_key=True)
    gist = database.Column(database.String(200), nullable=False)
    completed = database.Column(database.Integer, default=0)
    created = database.Column(database.DateTime, default=datetime.utcnow)
    details = database.Column(database.String(500), nullable=False)

    def __repr__(self):
        return "<Task %r>" % self.identity


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        taskgist = request.form["gist"]
        taskdetails = request.form["details"]
        newtask = Todo(gist=taskgist, details=taskdetails)
        try:
            database.session.add(newtask)
            database.session.commit()
            return redirect('/')
        except SQLAlchemyError:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.order_by(Todo.created).all()
        return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:identity>")
def delete(identity: int):
    deletetask = Todo.query.get_or_404(identity)
    try:
        database.session.delete(deletetask)
        database.session.commit()
        return redirect('/')
    except SQLAlchemyError:
        return "There was a problem deleting that task!"


@app.route("/edit/<int:identity>", methods=["POST", "GET"])
def edit(identity: int):
    updatetask = Todo.query.get_or_404(identity)
    if request.method == "POST":
        updatetask.gist = request.form["gist"]
        updatetask.details = request.form["details"]
        try:
            database.session.commit()
            return redirect('/')
        except SQLAlchemyError:
            return "There was an issue, updating your task"
    else:
        return render_template("edit.html", task=updatetask)


if __name__ == '__main__':
    app.run(debug=True)
