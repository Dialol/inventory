from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from prometheus_client import start_http_server, Counter, Gauge
import threading
from sqlalchemy.orm import Session
from database import SessionLocal, ItemModel

app = FastAPI()

ITEMS = Gauge('inventory_items_count', 'Number of items in inventory')
ITEMS_ADDED = Counter('items_added_total', 'Total number of items added')
ITEMS_REMOVED = Counter('items_removed_total', 'Total number of items removed')


class Item(BaseModel):
    name: str
    quantity: int


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    db: Session = SessionLocal()
    try:
        if db.query(ItemModel).filter(ItemModel.name == item.name).first():
            raise HTTPException(status_code=400, detail="Товар уже существует")
        db_item = ItemModel(name=item.name, quantity=item.quantity)
        db.add(db_item)
        db.commit()
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/items/", response_model=List[Item])
async def read_items():
    db: Session = SessionLocal()
    try:
        items = db.query(ItemModel).all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/items/{item_name}", response_model=Item)
async def read_item(item_name: str):
    db: Session = SessionLocal()
    try:
        item = db.query(ItemModel).filter(ItemModel.name == item_name).first()
        if not item:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.put("/items/{item_name}", response_model=Item)
async def update_item(item_name: str, item: Item):
    db: Session = SessionLocal()
    try:
        db_item = db.query(ItemModel).filter(
            ItemModel.name == item_name).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Товар не найден")
        old_quantity = db_item.quantity
        db_item.name = item.name
        db_item.quantity = item.quantity
        db.commit()

        if item.quantity > old_quantity:
            ITEMS_ADDED.inc()
        elif item.quantity < old_quantity:
            ITEMS_REMOVED.inc()

        ITEMS.set(db.query(ItemModel).count())
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.delete("/items/{item_name}", response_model=Item)
async def delete_item(item_name: str):
    db: Session = SessionLocal()
    try:
        db_item = db.query(ItemModel).filter(
            ItemModel.name == item_name).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Товар не найден")
        db.delete(db_item)
        db.commit()
        ITEMS.set(db.query(ItemModel).count())
        ITEMS_REMOVED.inc()
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


if __name__ == "__main__":
    def run_prometheus_server():
        start_http_server(8001)

    t = threading.Thread(target=run_prometheus_server)
    t.start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
