from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/todoapp2'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, default=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id', ondelete= 'CASCADE'), nullable = False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description} {self.list_id}>'

class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, default = False)
    todos = db.relationship('Todo', backref = 'todolist', passive_deletes=True, lazy = True, cascade = 'all, delete-orphan')


@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.json['description']
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return jsonify(body)

@app.route('/todolists/create', methods=['POST'])
def create_todolist():
  error = False
  body = {}
  try:
    name = request.json['name']
    todolist = TodoList(name=name)
    db.session.add(todolist)
    db.session.commit()
    body['name'] = todolist.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.json['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('get_list_todos', list_id=todo.todolist))

@app.route('/todolists/<todolist_id>/set-completed', methods=['POST'])
def set_completed_todolist(todolist_id):
    try:
        completed = request.json['completed']
        todolist = TodoList.query.get(todolist_id)
        todolist.completed = completed
        for todo in todolist.todos:
            todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index2'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify ({"success": True})

@app.route('/todolists/<todolist_id>', methods=['DELETE'])
def delete_todolist(todolist_id):
    try:
        todo_list = TodoList.query.filter_by(id=todolist_id).one()
        db.session.delete(todo_list)
        db.session.commit()
    except:
        print(str(todolist_id) + "not deleted")
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify ({"success": True})

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html', data=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index2():
    return render_template('index2.html', data=TodoList.query.order_by('id').all())

if __name__ == '__main__' :
    app.run(debug = True)
