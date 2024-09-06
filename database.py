from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    quantity = Column(Integer)


def init_db():
    Base.metadata.create_all(bind=engine)
    db_file = "test.db"
    if os.path.exists(db_file):
        print(f"{db_file} успешно создана.")
    else:
        print(f"Ошибка в создании {db_file}")


if __name__ == "__main__":
    init_db()
