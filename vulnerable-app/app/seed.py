from .database import SessionLocal
from .models import User, StoredData


def seed_database():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        users = [
            User(username="admin", password="supersecret123", role="admin"),
            User(username="operator", password="password123", role="user"),
            User(username="guest", password="guest", role="user"),
        ]
        db.add_all(users)

        secrets = [
            StoredData(owner="admin", secret="FLAG{sql1t3_1nj3ct10n}", note="Database credentials"),
            StoredData(owner="admin", secret="sk-1234-fake-api-key", note="API key for external service"),
            StoredData(owner="operator", secret="Credit card: 4111-1111-1111-1111", note="Test card data"),
            StoredData(owner="guest", secret="guest:guest", note="Guest credentials backup"),
        ]
        db.add_all(secrets)
        db.commit()
    finally:
        db.close()
