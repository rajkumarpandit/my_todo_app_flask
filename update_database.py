from app import app, db
from database import Todo
from sqlalchemy import text
from datetime import datetime

def update_database():
    with app.app_context():
        # Get the database connection
        connection = db.engine.connect()
        
        try:
            # Check if target_date column exists
            result = connection.execute(text("PRAGMA table_info(todo)"))
            columns = [row[1] for row in result]
            
            # Add target_date column if it doesn't exist
            if 'target_date' not in columns:
                # First add the column without default
                connection.execute(text("ALTER TABLE todo ADD COLUMN target_date DATETIME"))
                # Then update existing rows with current timestamp
                connection.execute(text("UPDATE todo SET target_date = created_at WHERE target_date IS NULL"))
                print("Added target_date column")
            
            # Add completed_at column if it doesn't exist
            if 'completed_at' not in columns:
                connection.execute(text("ALTER TABLE todo ADD COLUMN completed_at DATETIME"))
                print("Added completed_at column")
            
            # Update existing completed todos with completion timestamp
            todos = Todo.query.filter_by(completed=True).all()
            for todo in todos:
                if not todo.completed_at:
                    todo.completed_at = todo.created_at
            db.session.commit()
            print("Updated existing completed todos with completion timestamps")
            
            print("Database update completed successfully!")
            
        except Exception as e:
            print(f"Error updating database: {str(e)}")
            db.session.rollback()
        finally:
            connection.close()

if __name__ == '__main__':
    update_database() 