from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User, Todo, get_local_time, get_system_timezone
from datetime import datetime
from sqlalchemy import text
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dadgdf444dgagafg13dgfdbvcb65767hjgjgj#1kjkll--56'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)


# Create tables and ensure schema
with app.app_context():
    db.create_all()
    

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_user_by_email(email)
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('today_todos'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.get_user_by_username(username):
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
            
        if User.get_user_by_email(email):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        User.create_user(username, email, hashed_password)
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/todos/<period>')
@login_required
def todos(period):
    todos = Todo.get_todos_by_period(current_user.id, period)
    return render_template('todos.html', 
                         todos=todos, 
                         period=period,
                         get_system_timezone=get_system_timezone)

@app.route('/todos/today')
@login_required
def today_todos():
    return todos('today')

@app.route('/todos/yesterday')
@login_required
def yesterday_todos():
    return todos('yesterday')

@app.route('/todos/this-week')
@login_required
def this_week_todos():
    return todos('this-week')

@app.route('/todos/last-week')
@login_required
def last_week_todos():
    return todos('last-week')

@app.route('/todos/this-month')
@login_required
def this_month_todos():
    return todos('this-month')

@app.route('/todos/older')
@login_required
def older_todos():
    return todos('older')

@app.route('/add_todo', methods=['POST'])
@login_required
def add_todo():
    content = request.form.get('content')
    if content:
        Todo.create_todo(current_user.id, content)
    return redirect(url_for('today_todos'))

@app.route('/edit_todo/<int:id>', methods=['POST'])
@login_required
def edit_todo(id):
    content = request.form.get('content')
    target_date = request.form.get('target_date')
    if content:
        if target_date:
            # Convert the input datetime to system timezone
            local_tz = get_system_timezone()
            target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
            target_date = target_date.astimezone(local_tz)
        Todo.update_todo(id, content, target_date)
    return redirect(url_for('today_todos'))

@app.route('/complete_todo/<int:id>')
@login_required
def complete_todo(id):
    Todo.toggle_todo_status(id)
    return redirect(request.referrer or url_for('today_todos'))

@app.route('/delete_todo/<int:id>')
@login_required
def delete_todo(id):
    Todo.delete_todo(id)
    return redirect(request.referrer or url_for('today_todos'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)