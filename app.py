from datetime import datetime

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
database = SQLAlchemy(app)


class Todo(database.Model):
    identity = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(200), nullable=False)
    completed = database.Column(database.Integer, default=0)
    created = database.Column(database.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.identity


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        taskcontent = request.form["content"]
        newtask = Todo(content=taskcontent)
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


@app.route("/update/<int:identity>", methods=["POST", "GET"])
def update(identity: int):
    updatetask = Todo.query.get_or_404(identity)
    if request.method == "POST":
        updatetask.content = request.form["content"]
        try:
            database.session.commit()
            return redirect('/')
        except SQLAlchemyError:
            return "There was an issue, updating your task"
    else:
        return render_template("update.html", task=updatetask)


if __name__ == '__main__':
    app.run(debug=True)
