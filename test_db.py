from db.database import SessionLocal, engine
from sqlalchemy import text


def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("Database is connected!")
    except Exception as e:
        print("Database connection failed!")
        print(str(e))


test_connection()
