from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import time
import pytz

db = SQLAlchemy()

def get_system_timezone():
    # Get system timezone name
    system_timezone = time.tzname[0]
    try:
        # Try to get the timezone object
        return pytz.timezone(system_timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        # If system timezone is not recognized, fallback to local timezone
        return pytz.timezone('Asia/Kolkata')

def get_local_time():
    local_tz = get_system_timezone()
    return datetime.now(local_tz)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(username, email, password):
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user

class Todo(db.Model):
    __tablename__ = 'todo'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_local_time)
    target_date = db.Column(db.DateTime, default=get_local_time)
    completed_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def get_todo_by_id(todo_id):
        return Todo.query.get(todo_id)

    @staticmethod
    def create_todo(user_id, content, target_date=None):
        if target_date is None:
            target_date = get_local_time()
        todo = Todo(content=content, user_id=user_id, target_date=target_date)
        db.session.add(todo)
        db.session.commit()
        return todo

    @staticmethod
    def update_todo(todo_id, content, target_date=None):
        todo = Todo.get_todo_by_id(todo_id)
        if todo:
            todo.content = content
            if target_date is not None:
                todo.target_date = target_date
            db.session.commit()

    @staticmethod
    def toggle_todo_status(todo_id):
        todo = Todo.get_todo_by_id(todo_id)
        if todo:
            todo.completed = not todo.completed
            if todo.completed:
                todo.completed_at = get_local_time()
            else:
                todo.completed_at = None
            db.session.commit()

    @staticmethod
    def delete_todo(todo_id):
        todo = Todo.get_todo_by_id(todo_id)
        if todo:
            db.session.delete(todo)
            db.session.commit()

    @staticmethod
    def get_todos_by_period(user_id, period):
        now = get_local_time()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if period == 'today':
            return Todo.query.filter(
                Todo.user_id == user_id,
                Todo.created_at >= today
            ).order_by(Todo.created_at.desc()).all()
        
        elif period == 'yesterday':
            yesterday = today.replace(day=today.day - 1)
            return Todo.query.filter(
                Todo.user_id == user_id,
                Todo.created_at >= yesterday,
                Todo.created_at < today
            ).order_by(Todo.created_at.desc()).all()
        
        elif period == 'this-week':
            week_start = today.replace(day=today.day - today.weekday())
            return Todo.query.filter(
                Todo.user_id == user_id,
                Todo.created_at >= week_start
            ).order_by(Todo.created_at.desc()).all()
        
        elif period == 'last-week':
            week_start = today.replace(day=today.day - today.weekday())
            last_week_start = week_start.replace(day=week_start.day - 7)
            return Todo.query.filter(
                Todo.user_id == user_id,
                Todo.created_at >= last_week_start,
                Todo.created_at < week_start
            ).order_by(Todo.created_at.desc()).all()
        
        elif period == 'this-month':
            month_start = today.replace(day=1)
            return Todo.query.filter(
                Todo.user_id == user_id,
                Todo.created_at >= month_start
            ).order_by(Todo.created_at.desc()).all()
        
        else:  # older
            month_start = today.replace(day=1)
            return Todo.query.filter(
                Todo.user_id == user_id,
                Todo.created_at < month_start
            ).order_by(Todo.created_at.desc()).all() 