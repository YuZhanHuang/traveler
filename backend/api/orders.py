from flask import Blueprint, request

from backend.decorators import route, data_schema
from backend.orders.schema import order_schema
from backend.services import order_service

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@route(orders_bp, '/', methods=["POST"])
@data_schema(order_schema)
def create_bond():
    return order_service.create(**request.json)
