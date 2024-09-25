from datetime import datetime

from sqlalchemy.orm import relationship

from backend.core import db
from backend.helper import JsonSerializer


class Order(db.Model, JsonSerializer):
    __tablename__ = 'order'
    __json_hidden__ = ["created", "updated", "deleted", "uid"]

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(8), nullable=False)
    name = db.Column(db.Text, nullable=False, comment="訂單名稱")
    price = db.Column(db.Numeric(precision=18, scale=2), nullable=False, comment="訂單價格")
    currency = db.Column(db.String(3), nullable=False, comment="貨幣代碼")

    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    address = relationship('Address', back_populates='order', uselist=False)


class Address(db.Model, JsonSerializer):
    __tablename__ = 'address'
    __json_hidden__ = ["id", "order_id", "order", "created", "updated"]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.uid'), nullable=False)
    city = db.Column(db.Text, nullable=False, comment="城市")
    district = db.Column(db.Text, nullable=False, comment="區域")
    street = db.Column(db.Text, nullable=False, comment="街道")

    order = relationship('Order', back_populates='address')  # 保持 back_populates

    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)
