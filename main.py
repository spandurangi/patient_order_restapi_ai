import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, Request, HTTPException
from sqlalchemy.orm import Session
import fitz
from database import SessionLocal, engine, Base
from models import Order, UserActivityLog
from llm_inference import extract_patient_data

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")
async def log_user_activity(request: Request, call_next):
    response = await call_next(request)
    db = SessionLocal()
    log = UserActivityLog(
        path=str(request.url),
        method=request.method,
        user_ip=request.client.host
    )
    db.add(log)
    db.commit()
    db.close()
    return response

@app.post("/orders")
def create_order(first_name: str, last_name: str, date_of_birth: str, db: Session = Depends(get_db)):
    order = Order(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@app.get("/orders/{order_id}")
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "first_name": order.first_name,
        "last_name": order.last_name,
        "date_of_birth": order.date_of_birth
    }

@app.put("/orders/{order_id}")
def update_order(order_id: int, first_name: str, last_name: str, date_of_birth: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.first_name = first_name
    order.last_name = last_name
    order.date_of_birth = date_of_birth
    db.commit()
    db.refresh(order)
    return {
        "id": order.id,
        "first_name": order.first_name,
        "last_name": order.last_name,
        "date_of_birth": order.date_of_birth
    }

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"detail": "Order deleted"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    contents = await file.read()
    pdf_document = fitz.open(stream=contents, filetype="pdf")
    text = "".join([page.get_text() for page in pdf_document])
    extracted_data = extract_patient_data(text)

    order = Order(
        first_name=extracted_data.get("first_name"),
        last_name=extracted_data.get("last_name"),
        date_of_birth=extracted_data.get("date_of_birth")
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {"order_id": order.id, **extracted_data}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
