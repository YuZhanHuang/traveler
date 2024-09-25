from flask import Blueprint, request

from backend.decorators import route, data_schema, paginate, customized_query_filter
from backend.exceptions import ValidationError
from backend.orders.schema import order_schema
from backend.services import order_service

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@route(orders_bp, '/', methods=["POST"])
@data_schema(order_schema)
def create_order():
    return order_service.create(**request.json)


@route(orders_bp, '/', methods=["GET"])
@customized_query_filter(default_time_interval=False)
@paginate(20)
def get_order(filters):
    return order_service.search(filters)


@route(orders_bp, '/<pk>', methods=["GET"])
def get_single_order(pk):
    order = order_service.first(id=pk)
    if not order:
        raise ValidationError(msg="data not found")

    return order.to_json()

