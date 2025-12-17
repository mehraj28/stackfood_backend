@router.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    new_order = Order(
        total_amount=order.total_amount,
        items=json.dumps(order.items)
    )
    db.add(new_order)
    db.commit()
    return {"message": "Order placed"}
