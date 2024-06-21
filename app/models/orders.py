from app import db
from datetime import datetime
from app.models.inventory import Batch

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    tin = db.Column(db.String(50), nullable=False)  # Added TIN field
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.name}>'

    def create_customer(name, email, phone=None):
        customer = Customer(name=name, email=email, phone=phone)
        db.session.add(customer)
        db.session.commit()
        return customer.id

    def get_customer(customer_id):
        return Customer.query.get(customer_id)

    def update_customer(customer_id, name=None, email=None, phone=None):
        customer = Customer.query.get(customer_id)
        if customer:
            if name:
                customer.name = name
            if email:
                customer.email = email
            if phone:
                customer.phone = phone
            db.session.commit()
        return customer

    def delete_customer(customer_id):
        customer = Customer.query.get(customer_id)
        if customer:
            db.session.delete(customer)
            db.session.commit()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    items = db.relationship('OrderItem', back_populates='order', lazy=True, cascade="all, delete-orphan")

    def update_total_amount(self):
        # print(self.items)
        # print(f"Order ID: {self.id}, Customer ID: {self.customer_id}")
        # print("Items in Order:")
        # for item in self.items:
        #     print(f"OrderItem ID: {item.id}, Batch ID: {item.batch_id}, Quantity: {item.quantity}")
        
        total_amount = sum(item.calculate_total_price() for item in self.items)
        self.total_amount = total_amount
        
        # print(f"Calculated Total Amount: {self.total_amount}")
        db.session.commit()

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship('Order', back_populates='items')
    batch = db.relationship('Batch', backref='order_items')
    
    
    def calculate_total_price(self):
        try:
            # print(f"Calculating total_price for OrderItem {self.id}")
            # print(f"Batch ID: {self.batch_id}, Quantity: {self.quantity}")

            batch = Batch.query.get(self.batch_id)
            # print(batch)  # Print batch object for debugging

            if batch:
                # print(f"Batch found: Batch Price: {batch.unit_price}")
                total_price = batch.unit_price * int(self.quantity)
                # print(f'total price: {total_price}')
                
                return total_price
            else:
                print("No batch found")
                return 0.0
        except Exception as e:
            print(f"Error fetching Batch: {e}")
            return 0.0  # Handle error gracefully


    @classmethod
    def create(cls, order_id, batch_id, quantity):
        order_item = cls(order_id=order_id, batch_id=batch_id, quantity=quantity)
        db.session.add(order_item)
        db.session.commit()
        return order_item

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<OrderItem {self.id}>'
