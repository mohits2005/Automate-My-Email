from app.database.database import Base, engine

from app.models.user import User
from app.models.email import Email


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")