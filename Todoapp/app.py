from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable = False, default =False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description} {self.completed}>'

#db.create_all()<--needed in the absence of migrate (which takes care of all changes)

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    try:
      description = request.form.get('description', '')
      todo = Todo(description=description)
      db.session.add(todo)
      db.session.commit()
    except:
        error = True
        db.session.rollback()
        print (sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
         return redirect(url_for('index'))

@app.route('/')
def index():
  return render_template('index.html', data=Todo.query.all())

if __name__=='__main__':
    app.run (debug=True)
