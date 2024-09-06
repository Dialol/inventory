from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, ItemModel

fake = Faker('ru-RU')


def populate_inventory(num_items: int, db: Session):
    for _ in range(num_items):
        name = fake.word()
        quantity = fake.random_int(min=1, max=100)
        item = ItemModel(name=name, quantity=quantity)
        try:
            db.add(item)
            db.commit()
        except IntegrityError:
            db.rollback()
            continue


def main():
    db = SessionLocal()
    try:
        populate_inventory(100, db)
        print("Данные успешно добавлены в базу данных")
    except Exception as e:
        print(f"Ошибка при добавлении данных: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
